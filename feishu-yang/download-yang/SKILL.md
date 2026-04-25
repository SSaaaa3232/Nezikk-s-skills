---
name: download-yang
description: Download recent Feishu files sent by Yang. Lists recent candidate files first, asks for selection indices, then downloads only the confirmed message IDs.
---

# Download Yang

## Overview

Use the shared CLI script to find recent Yang file messages, confirm user selection by index, and download only confirmed files.

CLI path:
- `feishu-yang/feishu-yang-automation/scripts/feishu_yang_cli.py`
- Keep the sibling folder `feishu-yang-automation/` installed with this skill.

## Workflow

1. List recent candidates in JSON:
- `python3 feishu-yang/feishu-yang-automation/scripts/feishu_yang_cli.py list-recent-files --json`

2. Present numbered candidates to the user.
- Show each item with index, `file_name`, `message_id`, and `create_time` when present.

3. Ask the user which indices to download.
- Accept comma and range input such as `1,3-5`.
- Confirm the resolved message IDs before downloading.

4. Download only confirmed message IDs:
- `python3 feishu-yang/feishu-yang-automation/scripts/feishu_yang_cli.py download-files --hours <N> --message-id <id1> --message-id <id2>`

5. Report downloaded paths from CLI output.

## Input Rules

- If no recent files are returned, tell the user and stop.
- Never guess indices or message IDs.
- If the user input is ambiguous, ask for a corrected selection.

## Environment

Required:
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_YANG_CHAT_ID`

Optional:
- `FEISHU_YANG_SENDER_NAME`
- `FEISHU_YANG_SENDER_OPEN_ID`
- `FEISHU_API_BASE`
- `FEISHU_HTTP_TIMEOUT`
