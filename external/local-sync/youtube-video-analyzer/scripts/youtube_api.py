"""
Zero-dependency YouTube API module.
Fetches transcripts and comments using only Python standard library.
"""

import http.cookiejar
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape
from time import sleep


# ──────────────────────────────────────────────────────────
#  Shared helpers
# ──────────────────────────────────────────────────────────

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

_INNERTUBE_ANDROID_CONTEXT = {
    "client": {
        "clientName": "ANDROID",
        "clientVersion": "20.10.38",
    }
}


def _make_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _build_opener():
    cj = http.cookiejar.CookieJar()
    ssl_handler = urllib.request.HTTPSHandler(context=_make_ssl_context())
    opener = urllib.request.build_opener(ssl_handler, urllib.request.HTTPCookieProcessor(cj))
    return opener, cj


def _get(opener, url, headers=None):
    hdrs = {"User-Agent": _USER_AGENT, "Accept-Language": "en-US"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    resp = opener.open(req, timeout=30)
    return resp.read().decode("utf-8")


def _post_json(opener, url, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": _USER_AGENT,
            "Content-Type": "application/json",
            "Accept-Language": "en-US",
        },
    )
    resp = opener.open(req, timeout=30)
    return json.loads(resp.read().decode("utf-8"))


def _search_dict(d, key):
    """DFS search for all values of a given key in nested dicts/lists."""
    results = []
    stack = [d]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for k, v in current.items():
                if k == key:
                    results.append(v)
                else:
                    stack.append(v)
        elif isinstance(current, list):
            stack.extend(current)
    return results


# ──────────────────────────────────────────────────────────
#  Transcript API
# ──────────────────────────────────────────────────────────

class TranscriptSnippet:
    __slots__ = ("text", "start", "duration")

    def __init__(self, text, start, duration):
        self.text = text
        self.start = start
        self.duration = duration


class TranscriptInfo:
    """Metadata about one available transcript track."""

    def __init__(self, language, language_code, is_generated, base_url, opener):
        self.language = language
        self.language_code = language_code
        self.is_generated = is_generated
        self._base_url = base_url
        self._opener = opener

    def fetch(self):
        """Fetch and parse the transcript XML, returning list of TranscriptSnippet."""
        raw = _get(self._opener, self._base_url)
        return _parse_transcript_xml(raw)

    def __repr__(self):
        kind = "auto-generated" if self.is_generated else "manual"
        return f"{self.language} ({self.language_code}) [{kind}]"


def _parse_transcript_xml(raw):
    """Parse YouTube timedtext XML into a list of TranscriptSnippet."""
    html_tag_re = re.compile(r"<[^>]*>", re.IGNORECASE)
    root = ET.fromstring(raw)
    snippets = []
    for elem in root.iter("text"):
        text = elem.text or ""
        text = unescape(text)
        text = html_tag_re.sub("", text)
        start = float(elem.attrib.get("start", "0"))
        dur = float(elem.attrib.get("dur", "0"))
        snippets.append(TranscriptSnippet(text, start, dur))
    return snippets


def list_transcripts(video_id):
    """
    Fetch all available transcript tracks for a video.
    Returns (manual_transcripts, generated_transcripts, translation_languages).
    Each transcript is a TranscriptInfo object.
    """
    opener, _cj = _build_opener()

    # 1. Fetch watch page to get INNERTUBE_API_KEY
    html = _get(opener, f"https://www.youtube.com/watch?v={video_id}")
    html = unescape(html)

    # Handle consent page
    if 'action="https://consent.youtube.com/s"' in html:
        m = re.search(r'name="v" value="(.*?)"', html)
        if m:
            # Set consent cookie and refetch
            ck = http.cookiejar.Cookie(
                version=0, name="CONSENT", value=f"YES+{m.group(1)}",
                port=None, port_specified=False,
                domain=".youtube.com", domain_specified=True, domain_initial_dot=True,
                path="/", path_specified=True,
                secure=False, expires=None, discard=True,
                comment=None, comment_url=None, rest={},
            )
            _cj.set_cookie(ck)
            html = _get(opener, f"https://www.youtube.com/watch?v={video_id}")
            html = unescape(html)

    key_match = re.search(r'"INNERTUBE_API_KEY":\s*"([a-zA-Z0-9_-]+)"', html)
    if not key_match:
        if "class=\"g-recaptcha\"" in html:
            raise RuntimeError("YouTube is blocking requests (CAPTCHA). Try again later.")
        raise RuntimeError("Could not extract INNERTUBE_API_KEY from watch page.")
    api_key = key_match.group(1)

    # 2. POST to InnerTube player endpoint
    player_url = f"https://www.youtube.com/youtubei/v1/player?key={api_key}"
    player_data = _post_json(opener, player_url, {
        "context": _INNERTUBE_ANDROID_CONTEXT,
        "videoId": video_id,
    })

    # 3. Check playability
    status = player_data.get("playabilityStatus", {})
    if status.get("status") != "OK":
        reason = status.get("reason", "Unknown error")
        raise RuntimeError(f"Video unavailable: {reason}")

    # 4. Parse caption tracks
    captions = player_data.get("captions", {})
    renderer = captions.get("playerCaptionsTracklistRenderer", {})
    tracks = renderer.get("captionTracks", [])

    if not tracks:
        raise RuntimeError("No transcripts available for this video.")

    manual = []
    generated = []
    for t in tracks:
        name_runs = t.get("name", {}).get("runs", [])
        lang_name = name_runs[0]["text"] if name_runs else t.get("name", {}).get("simpleText", "")
        lang_code = t.get("languageCode", "")
        is_gen = t.get("kind") == "asr"
        base_url = t.get("baseUrl", "").replace("&fmt=srv3", "")

        info = TranscriptInfo(lang_name, lang_code, is_gen, base_url, opener)
        if is_gen:
            generated.append(info)
        else:
            manual.append(info)

    # Translation languages
    trans_langs = []
    for tl in renderer.get("translationLanguages", []):
        name_runs = tl.get("languageName", {}).get("runs", [])
        name = name_runs[0]["text"] if name_runs else ""
        code = tl.get("languageCode", "")
        trans_langs.append((name, code))

    return manual, generated, trans_langs


def find_transcript(video_id, language_codes):
    """
    Find the best transcript for the given language priority list.
    Tries manual transcripts first, then auto-generated.
    Returns a TranscriptInfo object.
    """
    manual, generated, _trans = list_transcripts(video_id)
    all_tracks = manual + generated

    # Try each requested language
    for lang in language_codes:
        for t in all_tracks:
            if t.language_code == lang:
                return t

    # Fallback: try partial match (e.g. "zh-Hans" matches "zh-Hans")
    for lang in language_codes:
        for t in all_tracks:
            if t.language_code.startswith(lang.split("-")[0]):
                return t

    # Last resort: return first available
    if all_tracks:
        return all_tracks[0]

    raise RuntimeError(f"No transcript found for languages: {language_codes}")


# ──────────────────────────────────────────────────────────
#  Comments API
# ──────────────────────────────────────────────────────────

SORT_BY_POPULAR = 0
SORT_BY_RECENT = 1

# Regex patterns for extracting ytcfg and ytInitialData
_YT_CFG_RE = re.compile(r"ytcfg\.set\s*\(\s*({.+?})\s*\)\s*;")
_YT_INITIAL_DATA_RE = re.compile(
    r'(?:window\s*\[\s*["\']ytInitialData["\']\s*\]|ytInitialData)\s*=\s*({.+?})\s*;\s*(?:var\s+meta|</script|\n)'
)

_COMMENT_TARGETS = {
    "comments-section",
    "engagement-panel-comments-section",
    "shorts-engagement-panel-comments-section",
}


def _extract_ytcfg(html):
    """Extract ytcfg.set({...}) config from page HTML."""
    for m in _YT_CFG_RE.finditer(html):
        try:
            cfg = json.loads(m.group(1))
            if "INNERTUBE_API_KEY" in cfg:
                return cfg
        except json.JSONDecodeError:
            continue
    return None


def _extract_initial_data(html):
    """Extract ytInitialData from page HTML."""
    m = _YT_INITIAL_DATA_RE.search(html)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return None


def _comment_ajax(opener, endpoint, ytcfg, retries=5):
    """Make InnerTube continuation AJAX call for comments."""
    cmd_meta = endpoint.get("commandMetadata", {}).get("webCommandMetadata", {})
    api_url = cmd_meta.get("apiUrl", "/youtubei/v1/next")

    cont_cmd = endpoint.get("continuationCommand", {})
    token = cont_cmd.get("token", "")

    api_key = ytcfg.get("INNERTUBE_API_KEY", "")
    context = ytcfg.get("INNERTUBE_CONTEXT", {})

    url = f"https://www.youtube.com{api_url}?key={api_key}"
    body = {"context": context, "continuation": token}

    for attempt in range(retries):
        try:
            return _post_json(opener, url, body)
        except urllib.error.HTTPError as e:
            if e.code in (403, 413):
                return {}
            if attempt < retries - 1:
                sleep(min(20, 2 ** attempt))
            else:
                return {}
        except Exception:
            if attempt < retries - 1:
                sleep(min(20, 2 ** attempt))
            else:
                return {}


def download_comments(video_id, sort_by=SORT_BY_POPULAR, limit=None):
    """
    Generator that yields comment dicts from a YouTube video.
    Each comment dict has: cid, text, time, author, channel, votes, photo, heart, reply.
    """
    opener, cj = _build_opener()

    # Pre-set consent cookie
    ck = http.cookiejar.Cookie(
        version=0, name="CONSENT", value="YES+cb",
        port=None, port_specified=False,
        domain=".youtube.com", domain_specified=True, domain_initial_dot=True,
        path="/", path_specified=True,
        secure=False, expires=None, discard=True,
        comment=None, comment_url=None, rest={},
    )
    cj.set_cookie(ck)

    url = f"https://www.youtube.com/watch?v={video_id}"
    html = _get(opener, url)

    ytcfg = _extract_ytcfg(html)
    if not ytcfg:
        raise RuntimeError("Could not extract ytcfg from watch page.")

    initial_data = _extract_initial_data(html)
    if not initial_data:
        raise RuntimeError("Could not extract ytInitialData from watch page.")

    # Find sort menu and initial continuation
    item_sections = _search_dict(initial_data, "itemSectionRenderer")
    sort_menu = _search_dict(initial_data, "sortFilterSubMenuRenderer")

    # Get sort-specific continuation endpoint
    if sort_menu:
        menu_items = sort_menu[0].get("subMenuItems", [])
        if sort_by < len(menu_items):
            endpoint = menu_items[sort_by].get("serviceEndpoint", {})
        else:
            endpoint = menu_items[0].get("serviceEndpoint", {})
    else:
        # Fallback: find first continuation from itemSectionRenderer
        conts = _search_dict(initial_data, "continuationEndpoint")
        if not conts:
            conts = _search_dict(initial_data, "continuationCommand")
        if conts:
            endpoint = conts[0] if isinstance(conts[0], dict) and "continuationCommand" in conts[0] else {"continuationCommand": conts[0]}
        else:
            return

    count = 0
    queue = [endpoint]

    while queue:
        ep = queue.pop(0)
        response = _comment_ajax(opener, ep, ytcfg)
        if not response:
            continue

        # Find next continuations
        reload_actions = _search_dict(response, "reloadContinuationItemsCommand")
        append_actions = _search_dict(response, "appendContinuationItemsAction")

        for action in reload_actions + append_actions:
            target = action.get("targetId", "")
            if target in _COMMENT_TARGETS or not target:
                cont_items = action.get("continuationItems", [])
                for item in cont_items:
                    cont_ep = _search_dict(item, "continuationEndpoint")
                    btn_ep = _search_dict(item, "buttonRenderer")
                    if cont_ep:
                        queue.insert(0, cont_ep[0])
                    # "Show more replies" button
                    for btn in btn_ep:
                        cmd = btn.get("command", {})
                        cont_cmd = _search_dict(cmd, "continuationCommand")
                        if cont_cmd:
                            queue.append({"continuationCommand": cont_cmd[0]})

        # Extract comments from entity payloads
        comment_entities = _search_dict(response, "commentEntityPayload")
        toolbar_states = _search_dict(response, "engagementToolbarStateEntityPayload")

        # Build heart state map
        heart_map = {}
        for ts in toolbar_states:
            key = ts.get("key", "")
            hearted = ts.get("heartState", "") == "TOOLBAR_HEART_STATE_HEARTED"
            if key:
                heart_map[key] = hearted

        for ce in comment_entities:
            props = ce.get("properties", {})
            author_info = ce.get("author", {})
            toolbar = ce.get("toolbar", {})

            cid = props.get("commentId", "")
            toolbar_key = props.get("toolbarStateKey", "")

            comment = {
                "cid": cid,
                "text": props.get("content", {}).get("content", ""),
                "time": props.get("publishedTime", ""),
                "author": author_info.get("displayName", ""),
                "channel": author_info.get("channelId", ""),
                "votes": toolbar.get("likeCountNotliked", "0") or "0",
                "photo": author_info.get("avatarThumbnailUrl", ""),
                "heart": heart_map.get(toolbar_key, False),
                "reply": "." in cid,
            }

            yield comment
            count += 1
            if limit and count >= limit:
                return
