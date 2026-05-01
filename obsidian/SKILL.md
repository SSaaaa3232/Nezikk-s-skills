---
name: obsidian
description: Use when the user enters /obsidian followed by an X/Twitter article link, to open the link with bb-browser using the user's logged-in browser state and save it into the local Obsidian vault with Obsidian Web Clipper.
---

# Obsidian

Use this skill when the user types `/obsidian` followed by a URL, especially an X/Twitter link.

Example:

```text
/obsidian https://x.com/example/status/1234567890
```

## Goal

Open the URL with `bb-browser` using the user's existing logged-in browser state, invoke Obsidian Web Clipper, and save the clipped article/page into the user's local Obsidian vault.

## Workflow

1. Parse the text after `/obsidian` as the target URL.
   - Require exactly one URL.
   - Accept `https://x.com/...`, `https://twitter.com/...`, and other article URLs.
   - If no URL is provided, ask the user for the URL.

2. Verify browser tooling before opening anything.
   - Check `bb-browser` is available.
   - If `bb-browser` is not available, stop and say it needs to be installed or configured.
   - Do not silently switch to a fresh browser session, because the point is to reuse the user's logged-in state.

3. Open the URL through `bb-browser`.
   - Use the user's existing local browser state.
   - Wait for the page to load.
   - If the page requires login and the session is not logged in, stop and ask the user to log in through the browser state used by `bb-browser`.

4. Trigger Obsidian Web Clipper.
   - Prefer the installed Obsidian Web Clipper extension button or configured browser action.
   - Confirm the clipper preview contains the expected page title/content.
   - Save into the default local Obsidian vault unless the user specifies a different vault or folder.

5. Verify the save.
   - Confirm the clipper reports success, or verify a new/updated Markdown file appears in the local Obsidian vault.
   - If possible, report the saved note path.

6. Report the result.
   - URL clipped
   - note title or saved path
   - any login/clipper issue encountered

## Safety Rules

- Do not post, like, reply, follow, or otherwise interact with X/Twitter content.
- Do not scrape private content into Obsidian unless the user explicitly gave that link and requested clipping.
- Do not use unauthenticated fetch/curl as a replacement for `bb-browser` when the page needs the user's logged-in state.
- Do not guess the vault path if Obsidian Web Clipper asks the user to choose a vault; ask the user to confirm.

## Fallbacks

If Obsidian Web Clipper is unavailable:

1. Stop and report that the extension is missing or inaccessible.
2. Ask the user whether to install/configure Obsidian Web Clipper or provide another capture method.
3. Do not create a manual Markdown note unless the user explicitly asks for manual fallback.
