#!/usr/bin/env python3
"""
YouTube Video Full Analyzer
Combines transcript (with timestamps) + comments for comprehensive analysis.

Usage:
  python analyze_video.py <video_id_or_url> [options]

Options:
  --mode full              Full analysis: transcript + comments (default)
  --mode transcript-only   Analyze transcript content only
  --mode comments-only     Analyze comment sentiment only
  --lang LANG              Transcript language (default: en, use zh-Hans for Chinese)
  --comment-limit N        Max number of comments to download (default: 500)
  --save                   Save transcript as .srt file + comments as .json file
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from utils import extract_video_id, seconds_to_hms
from youtube_api import find_transcript, download_comments as _download, SORT_BY_POPULAR


def _format_srt(entries):
    """Format transcript entries as SRT subtitle format."""
    lines = []
    for i, e in enumerate(entries, 1):
        start = seconds_to_hms(e.start)
        end = seconds_to_hms(e.start + e.duration)
        lines.append(f"{i}")
        lines.append(f"{start} --> {end}")
        lines.append(e.text)
        lines.append("")
    return "\n".join(lines)


def get_transcript(video_id: str, language: str, save: bool = False) -> dict | None:
    try:
        priority = list(dict.fromkeys([language, "en"]))
        transcript = find_transcript(video_id, priority)
        entries = transcript.fetch()
        lang_code = transcript.language_code

        timestamped_lines = [
            f"[{seconds_to_hms(e.start).replace(',', '.')}] {e.text}"
            for e in entries
        ]
        timestamped_text = "\n".join(timestamped_lines)

        if save:
            srt_content = _format_srt(entries)
            srt_filename = f"{video_id}_transcript_{lang_code}.srt"
            with open(srt_filename, "w", encoding="utf-8") as f:
                f.write(srt_content)
            print(f"SRT saved: {srt_filename}", file=sys.stderr)

        return {
            "language": transcript.language,
            "language_code": lang_code,
            "is_generated": transcript.is_generated,
            "total_snippets": len(entries),
            "plain_text": " ".join(e.text for e in entries),
            "timestamped_text": timestamped_text,
        }

    except Exception as e:
        print(f"Transcript unavailable: {type(e).__name__}: {e}", file=sys.stderr)
        return None


def get_comments(video_id: str, limit: int, save: bool = False) -> dict | None:
    try:
        print(f"Downloading up to {limit} comments...", file=sys.stderr)
        raw = list(_download(video_id, sort_by=SORT_BY_POPULAR, limit=limit))
        print(f"Downloaded {len(raw)} comments", file=sys.stderr)

        def parse_votes(v):
            v = str(v).strip().replace(",", "")
            try:
                if v.endswith("K"): return int(float(v[:-1]) * 1000)
                if v.endswith("M"): return int(float(v[:-1]) * 1_000_000)
                return int(v)
            except (ValueError, AttributeError): return 0

        comments = [
            {
                "author": c.get("author", ""),
                "text": c.get("text", ""),
                "votes": c.get("votes", "0"),
                "votes_int": parse_votes(c.get("votes", 0)),
                "time": c.get("time", ""),
                "heart": c.get("heart", False),
                "reply": c.get("reply", False),
            }
            for c in raw
        ]

        top = sorted(comments, key=lambda c: c["votes_int"], reverse=True)[:20]

        result = {
            "total_downloaded": len(comments),
            "top_comments": top,
            "sample_recent": comments[:50],
            "all_comments": comments,
        }

        if save:
            fname = f"{video_id}_comments.json"
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"Comments saved: {fname}", file=sys.stderr)

        return result

    except Exception as e:
        print(f"Comments unavailable: {type(e).__name__}: {e}", file=sys.stderr)
        return None


def print_report(video_id: str, transcript: dict | None, comments: dict | None):
    url = f"https://www.youtube.com/watch?v={video_id}"
    sep = "=" * 70

    print(f"\n{sep}")
    print(f"  YOUTUBE VIDEO ANALYSIS REPORT")
    print(f"{sep}")
    print(f"  Video ID : {video_id}")
    print(f"  URL      : {url}")

    if transcript:
        print(f"\n  TRANSCRIPT INFO")
        print(f"  Language : {transcript['language']} ({transcript['language_code']})")
        print(f"  Source   : {'Auto-generated' if transcript['is_generated'] else 'Manual'}")
        print(f"  Snippets : {transcript['total_snippets']}")
        print(f"  Length   : {len(transcript['plain_text'])} chars")
        print(f"\n{'-'*70}")
        print(f"  TIMESTAMPED TRANSCRIPT (for Agent analysis):\n")
        print(transcript["timestamped_text"][:14000])
        if len(transcript["timestamped_text"]) > 14000:
            total = len(transcript["timestamped_text"])
            print(f"\n  ... [truncated at 14000 chars, total {total} chars]")
    else:
        print(f"\n  TRANSCRIPT: Not available")

    if comments:
        print(f"\n{sep}")
        print(f"  COMMENTS DATA")
        print(f"{sep}")
        print(f"  Total downloaded : {comments['total_downloaded']}")

        print(f"\n  TOP 20 COMMENTS (by votes):")
        print(f"{'-'*70}")
        for i, c in enumerate(comments["top_comments"], 1):
            heart = "[heart] " if c["heart"] else ""
            print(f"\n  #{i:02d} [{c['votes']} votes] {heart}{c['author']} - {c['time']}")
            print(f"      {c['text'][:300]}{'...' if len(c['text']) > 300 else ''}")

        print(f"\n{'-'*70}")
        print(f"  SAMPLE: 50 Recent Comments:")
        print(f"{'-'*70}")
        for i, c in enumerate(comments["sample_recent"], 1):
            print(f"\n  #{i:02d} [{c['votes']} votes] {c['author']} - {c['time']}")
            print(f"      {c['text'][:200]}{'...' if len(c['text']) > 200 else ''}")
    else:
        print(f"\n  COMMENTS: Not available (disabled or error)")

    print(f"\n{sep}")
    print(f"  AGENT: Please produce the following structured report")
    print(f"       in the user's language:")
    print(f"{sep}")
    print("""
  1. Video Topic (one sentence)
  2. Content Summary (150-250 words, based on transcript)
  3. Key Takeaways (3-7 bullet points)
  4. Important Timestamps (cite [HH:MM:SS] from transcript)

  5. Sentiment Analysis (based on comments):
     - Overall sentiment (positive / neutral / negative percentage estimate)
     - Top Comments (Top 3-5, with original text and vote count)
     - Major audience feedback themes
     - Controversies or negative feedback (if any)

  6. Audience Profile
""")
    print(sep)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    video_input = sys.argv[1]
    video_id = extract_video_id(video_input)
    args = sys.argv[2:]

    mode = "full"
    if "--mode" in args:
        idx = args.index("--mode")
        mode = args[idx + 1] if idx + 1 < len(args) else "full"

    lang = "en"
    if "--lang" in args:
        idx = args.index("--lang")
        lang = args[idx + 1] if idx + 1 < len(args) else "en"

    comment_limit = 500
    if "--comment-limit" in args:
        idx = args.index("--comment-limit")
        try:
            comment_limit = int(args[idx + 1])
        except (IndexError, ValueError):
            pass

    save = "--save" in args

    transcript = None
    comments = None

    if mode in ("full", "transcript-only"):
        print(f"Fetching transcript (lang={lang})...", file=sys.stderr)
        transcript = get_transcript(video_id, lang, save=save)

    if mode in ("full", "comments-only"):
        comments = get_comments(video_id, comment_limit, save=save)

    print_report(video_id, transcript, comments)


if __name__ == "__main__":
    main()
