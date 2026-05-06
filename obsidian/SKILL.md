---
name: obsidian
description: Use when the user enters /obsidian followed by an X/Twitter/article URL, or provides an X/Twitter link while asking to save it to Obsidian. Open the link with bb-browser using the user's logged-in browser state, clip it with Obsidian Web Clipper, and save it into Obsidian-Template/raw/articles. This skill is especially important for X/Twitter posts/articles because the logged-in browser state and Web Clipper extraction are required.
---

# Obsidian

Use this skill when the user types `/obsidian` followed by a URL, especially an X/Twitter link. Also use it when the user provides an X/Twitter/article URL and the surrounding context says to save or clip it into Obsidian.

Example:

```text
/obsidian https://x.com/example/status/1234567890
```

## Goal

Open the URL with `bb-browser` using the user's existing logged-in browser state, invoke Obsidian Web Clipper, and save the clipped article/page into this local Obsidian folder:

```text
/Users/saaaaa/Obsidian-Template/raw/articles
```

## Workflow

1. Parse the text after `/obsidian` as the target URL.
   - Require exactly one URL.
   - Accept `https://x.com/...`, `https://twitter.com/...`, and other article URLs.
   - If no URL is provided, ask the user for the URL.

2. Verify browser tooling before opening anything.
   - Check `bb-browser` is available.
   - Confirm `/Users/saaaaa/Obsidian-Template/raw/articles` exists.
   - If `bb-browser` is not available, stop and say it needs to be installed or configured.
   - Do not silently switch to a fresh browser session, because the point is to reuse the user's logged-in state.

3. Open the URL through `bb-browser`.
   - Use the user's existing local browser state.
   - Wait for the page to load.
   - Keep the returned `Tab ID`; use it for later `snapshot`, `eval`, and verification commands.
   - If the page requires login and the session is not logged in, stop and ask the user to log in through the browser state used by `bb-browser`.
   - For X/Twitter, do not trust a sparse accessibility snapshot by itself. X often exposes only shell text in `snapshot` even when the post/article is loaded. Verify with:
     - `bb-browser eval 'document.body.innerText.slice(0,1000)' --tab <TAB_ID>`
     - `bb-browser network requests x.com --tab <TAB_ID>` if needed
   - Continue only when the target post/article text is visible in the DOM.

4. Open or refresh Obsidian Web Clipper.
   - Prefer the installed Obsidian Web Clipper extension button, side panel, or configured browser action.
   - Useful shortcuts from the extension:
     - `Command+Shift+O` opens the clipper.
     - `Alt+Shift+O` quick-clips.
   - If a Web Clipper side panel or popup tab is already open, inspect it instead of opening duplicates.
   - Confirm the clipper preview contains the expected page title, source URL, author, and content.
   - Check fields directly when possible:
     - `#note-name-field`
     - `#title`
     - `#source`
     - `#author`
     - `#note-content-field`
     - `#vault-select`
     - `#path-name-field`
   - Save into `raw/articles` in the local vault.
   - If the clipper asks for a vault, use `Obsidian-Template`.
   - If the clipper asks for a folder/path, use `raw/articles`.
   - The expected Obsidian Web Clipper settings are:
     - Vault: `Obsidian-Template`
     - Note location: `raw/articles`
     - Save behavior: `Add to Obsidian`

5. Fix stale Web Clipper previews before saving.
   - If the clipper preview shows a different page than the target URL, do not save.
   - This can happen when `bb-browser tab <index>` selects a tab for automation but Chrome's extension API still reports an older tab as active.
   - If a shortcut opens or refreshes an existing side panel attached to a different tab, inspect the extension fields before clicking save. A stale panel can keep `#source`, `#title`, and `#note-content-field` from the older X/Twitter page even after the target tab is visible in `bb-browser`.
   - From an Obsidian Web Clipper extension page, inspect Chrome's real active tab:

```javascript
chrome.tabs.query({}).then(tabs => tabs.map(t => ({
  id: t.id,
  active: t.active,
  url: t.url,
  title: t.title,
  windowId: t.windowId
})))
```

   - Find the Chrome tab whose `url` exactly matches the target URL, then activate it through the extension API:

```javascript
chrome.tabs.update(TARGET_CHROME_TAB_ID, { active: true })
```

   - Reload the Web Clipper side panel/popup after activating the correct Chrome tab.
   - Re-check `#source`, `#title`, and `#note-content-field`. The `#source` field must match the target URL before saving.
   - If `bb-browser` cannot address the Web Clipper side-panel iframe as a tab, use the browser's CDP target list to find the extension iframe whose URL contains `chrome-extension://.../side-panel.html?context=iframe`, then evaluate the field checks in that iframe target. The bb-browser daemon CDP port is visible in process args or daemon status; `curl http://127.0.0.1:<port>/json/list` lists page and iframe targets.
   - If the side panel remains attached to the wrong page, inject a fresh Web Clipper iframe into the target page instead of saving the stale preview:

```javascript
(() => {
  const old = document.getElementById("manual-obsidian-clipper");
  if (old) old.remove();
  const iframe = document.createElement("iframe");
  iframe.id = "manual-obsidian-clipper";
  iframe.src = "chrome-extension://cnjifjpddelmedmihgijeibhnjfabmlf/side-panel.html?context=iframe";
  Object.assign(iframe.style, {
    position: "fixed",
    right: "0",
    top: "0",
    width: "420px",
    height: "100vh",
    zIndex: "2147483647",
    border: "0",
    background: "white"
  });
  document.body.appendChild(iframe);
})();
```

   - After injecting a fresh iframe, use CDP target inspection again to verify `#source` equals the target URL and `#note-content-field` contains the expected X/Twitter article text before clicking `#clip-btn`.
   - Do not treat a direct `bb-browser open chrome-extension://.../popup.html` failure such as `ERR_BLOCKED_BY_CLIENT` as proof that Web Clipper is unavailable. Prefer the installed extension iframe or the extension side panel already loaded in the target page.

6. Save and verify.
   - Click `Add to Obsidian`.
   - Confirm the clipper reports success, verify the console exposes an `Obsidian URL:`, or verify a new/updated Markdown file appears in the local Obsidian vault.
   - If clicking `Add to Obsidian` produces no new/updated file and no `Obsidian URL:` in the relevant page/extension console, do not claim success. Report that the preview was correct but the handoff/save did not complete.
   - Verify the saved file is under `/Users/saaaaa/Obsidian-Template/raw/articles`.
   - Verify the saved Markdown frontmatter `source` matches the target URL.
   - Verify the body contains the expected article/post text, not only a clipboard troubleshooting message.
   - If possible, report the saved note path.

7. Report the result.
   - URL clipped
   - note title or saved path
   - any login/clipper issue encountered

## Safety Rules

- Do not post, like, reply, follow, or otherwise interact with X/Twitter content.
- Do not scrape private content into Obsidian unless the user explicitly gave that link and requested clipping.
- Do not use unauthenticated fetch/curl as a replacement for `bb-browser` when the page needs the user's logged-in state.
- Do not save outside `/Users/saaaaa/Obsidian-Template/raw/articles` unless the user explicitly asks for another folder.

## Fallbacks

If Obsidian Web Clipper generated the Markdown content but Chrome does not hand off the `obsidian://` URL to Obsidian, open the same Obsidian URI with the system `open` command. This is allowed because the content still comes from Web Clipper and the target remains `Obsidian-Template/raw/articles`.

Operational fallback:

1. After clicking `Add to Obsidian`, check the Web Clipper console for a line beginning with `Obsidian URL:`.
2. Use that exact generated `obsidian://...` URI with `open`.
   - If the URI contains `&clipboard&content=Obsidian%20is%20not%20able%20to%20access%20your%20clipboard...`, still open the exact URI. In practice, Chrome may have copied the real Web Clipper note body to the clipboard while using that `content=` value only as Obsidian's troubleshooting fallback.
   - Do not replace or "fix" the URI before opening it.
3. Do not synthesize a different URI unless the console did not expose one.
4. Re-verify the created Markdown file under `/Users/saaaaa/Obsidian-Template/raw/articles` by searching for the target `source` URL and expected body text.
5. If the created file contains only Obsidian clipboard troubleshooting text, report the failure instead of claiming success. If the file contains the target source and expected article/post body, treat the fallback as successful even though the console URI included the troubleshooting `content=` parameter.

If Obsidian Web Clipper is unavailable:

1. Stop and report that the extension is missing or inaccessible.
2. Ask the user whether to install/configure Obsidian Web Clipper or provide another capture method.
3. Do not create a manual Markdown note unless the user explicitly asks for manual fallback.
