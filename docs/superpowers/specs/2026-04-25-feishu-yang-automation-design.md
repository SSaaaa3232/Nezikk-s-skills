# Feishu Yang Automation Design

## Goal

Add two reusable skills to this repository for a fixed Feishu group:

- `/download-yang`: list file messages from the last 24 hours sent by a specific sender, ask the user which files to fetch, and download the chosen files into `~/Desktop/yang-downloads/<batch-dir>/`
- `/send-yang`: upload a local file and send it back to the same fixed group as a file message

The implementation must avoid a long-running listener. Both workflows are pull-based and start only when the user explicitly invokes the command.

## Scope

In scope:

- two discoverable skills in this repository
- one shared CLI script for Feishu API operations
- support for a fixed group ID provided later
- support for a fixed sender provided later
- recent-history lookup limited to the last 24 hours
- interactive confirmation before any download
- deterministic desktop download layout under `~/Desktop/yang-downloads/`

Out of scope:

- webhook-only custom group bots
- background daemons or event callbacks
- automatic batch detection without user confirmation
- support for multiple groups in the first version
- support for non-file message types in the first version

## User Experience

### `/download-yang`

1. The user invokes `/download-yang`.
2. The skill loads the shared Feishu CLI with the fixed group configuration.
3. The CLI queries recent messages for the target group and filters:
   - message type is file
   - message time is within the last 24 hours
   - sender matches the configured target sender
4. The skill presents a compact candidate list ordered by message time. Each row includes:
   - index
   - send time in local time
   - sender label
   - original file name
   - message ID
5. The skill asks the user whether to fetch files and which indices to include in this batch.
6. After confirmation, the CLI downloads the selected files into a new subdirectory under `~/Desktop/yang-downloads/`.
7. The skill reports the created directory and the saved files.

The first version does not auto-guess the batch. The user chooses the batch from the presented candidate list every time.

### `/send-yang`

1. The user invokes `/send-yang`.
2. The skill asks for the local file path if none was already provided in the prompt.
3. The CLI validates that the file exists and is readable.
4. The CLI uploads the file to Feishu.
5. The CLI sends a file message to the configured fixed group.
6. The skill reports success with the file name and target group identifier.

## Configuration Model

The implementation will separate code from secrets. Runtime values provided later will be read from environment variables or a local config file that is excluded from version control.

Required runtime values:

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_YANG_CHAT_ID`
- `FEISHU_YANG_SENDER_NAME` for a name-based first version

Optional later hardening:

- `FEISHU_YANG_SENDER_OPEN_ID`
- `FEISHU_BASE_URL` only if needed for testing or future compatibility

First release behavior:

- sender matching defaults to exact sender-name comparison
- if a stable sender ID is later supplied, the filtering layer should prefer that over sender name

## Proposed Repository Structure

- `download-yang/SKILL.md`
- `download-yang/agents/openai.yaml`
- `send-yang/SKILL.md`
- `send-yang/agents/openai.yaml`
- `feishu-yang-common/scripts/feishu_yang_cli.py`
- `feishu-yang-common/scripts/__init__.py` only if packaging is useful during implementation
- `tests/test_feishu_yang_cli.py`

The two skills should stay small. They describe the workflow and delegate API work to the shared script.

## Shared CLI Responsibilities

The shared CLI script will expose subcommands rather than embedding logic into the skill text.

Planned subcommands:

- `list-recent-files`
- `download-files`
- `send-file`

Planned responsibilities:

- fetch tenant access token
- call Feishu APIs with consistent headers and error handling
- list recent group messages and filter candidate file messages
- normalize message data for terminal presentation
- download file content to disk
- upload local files
- send file messages to the configured group

## Feishu API Flow

### Read path for `/download-yang`

1. Get tenant access token from app credentials.
2. Query recent messages for the configured group.
3. Filter to the last 24 hours, file messages, and the configured sender.
4. For each selected result, fetch or resolve the file resource metadata needed for download.
5. Download the file bytes to the chosen local directory.

### Write path for `/send-yang`

1. Get tenant access token from app credentials.
2. Upload the local file to Feishu and obtain the file key.
3. Send a `file` type message to the configured group using that file key.

The exact Feishu endpoint details can be finalized during implementation once the runtime credentials are available for verification. The public contract of the tool will stay unchanged.

## Download Directory Layout

Base directory:

- `~/Desktop/yang-downloads/`

Per-run batch directory format:

- `YYYYMMDD-HHMMSS-<short-label>`

`<short-label>` should be deterministic and human-readable. First choice:

- `yang-files`

Example:

- `~/Desktop/yang-downloads/20260425-143522-yang-files/`

Collision handling:

- if a directory already exists, append `-2`, `-3`, and so on

File handling:

- preserve original file names when possible
- if duplicate names exist within the same batch directory, append a numeric suffix before the extension

## Error Handling

The workflows should fail loudly and specifically.

Cases to handle:

- missing required credentials
- missing chat ID or sender filter
- no matching files found in the last 24 hours
- user declines download after seeing candidates
- selected indices are invalid
- target file path for `/send-yang` does not exist
- Feishu authentication failure
- Feishu API returns insufficient permission
- file download fails after partial progress
- file upload succeeds but message send fails

Response style:

- short explanation of what failed
- next corrective action when obvious
- no fake success states

## Testing Strategy

Unit coverage should focus on deterministic logic that does not require live credentials:

- timestamp cutoff filtering
- sender filtering
- file-message filtering
- batch directory naming
- duplicate filename resolution
- CLI argument parsing
- selection parsing for interactive download confirmation

Manual verification after credentials are provided:

1. run recent-file listing against the target group
2. confirm at least one candidate from the last 24 hours is shown
3. download a selected file into the desktop directory
4. send a local test file back to the target group

## Security and Repo Hygiene

- never commit `app_secret`
- keep runtime config out of git
- do not print raw tokens in normal output
- truncate or omit sensitive identifiers in user-facing logs when possible

## Open Decisions Already Settled

- fixed group in v1: yes
- recent window: 24 hours
- listener service: no
- automatic batch inference: no
- desktop root path: `~/Desktop/yang-downloads`
- command names: `/download-yang` and `/send-yang`

## Implementation Readiness

This design is ready for an implementation plan. The only missing runtime inputs are secrets and final identifiers, which are intentionally deferred until verification:

- Feishu app credentials
- fixed group `chat_id`
- sender identity value for filtering
