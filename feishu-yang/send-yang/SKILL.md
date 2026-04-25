---
name: send-yang
description: Send a local file to the Yang Feishu chat through the shared CLI. Ask for file path if missing, then run send-file.
---

# Send Yang

## Overview

Use the shared CLI to upload a local file and send it to the configured Yang chat.

CLI path:
- `feishu-yang/feishu-yang-automation/scripts/feishu_yang_cli.py`
- Keep the sibling folder `feishu-yang-automation/` installed with this skill.

## Workflow

1. Check whether the user already provided a local file path.
- If missing, ask for the path first.

2. Confirm the path looks local and accessible.
- If it does not exist, ask for a corrected path.

3. Send the file with CLI:
- `python3 feishu-yang/feishu-yang-automation/scripts/feishu_yang_cli.py send-file --path "<local-path>"`

4. Report success output from CLI.

## Input Rules

- `send-file` requires `--path`.
- Do not run the send command without a concrete path.
- If the path contains spaces, quote it in the command.

## Environment

Required:
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_YANG_CHAT_ID`

Optional:
- `FEISHU_API_BASE`
- `FEISHU_HTTP_TIMEOUT`
