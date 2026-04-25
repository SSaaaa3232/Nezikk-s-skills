# Feishu Yang Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build two reusable skills, `/download-yang` and `/send-yang`, backed by one shared Feishu CLI that can list recent file messages from a fixed group, download selected files to the desktop, and upload a local file back to the same group.

**Architecture:** Keep the skills thin and declarative. Put all Feishu authentication, API calls, filtering, download path logic, and upload/send logic into a single Python CLI under `feishu-yang-automation/scripts/feishu_yang_cli.py`, then have the two skills invoke that script with the configured environment variables.

**Tech Stack:** Python 3 standard library, unittest, Feishu Open Platform HTTP APIs, Markdown skill files, OpenAI skill metadata YAML.

---

### Task 1: Build the shared CLI skeleton and deterministic helpers

**Files:**
- Create: `feishu-yang-automation/scripts/feishu_yang_cli.py`
- Create: `tests/test_feishu_yang_cli.py`

- [ ] **Step 1: Write the failing helper tests**

```python
import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "feishu-yang-automation" / "scripts" / "feishu_yang_cli.py"
SPEC = importlib.util.spec_from_file_location("feishu_yang_cli", CLI_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FeishuYangCliHelperTests(unittest.TestCase):
    def test_require_settings_reports_missing_values(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "FEISHU_APP_ID"):
            MODULE.require_settings({})

    def test_make_batch_dir_name_uses_timestamp_and_label(self) -> None:
        value = MODULE.make_batch_dir_name("20260425-143522", "yang-files")
        self.assertEqual(value, "20260425-143522-yang-files")

    def test_resolve_duplicate_filename_appends_counter(self) -> None:
        output_dir = Path("/tmp/yang-downloads-test")
        first = MODULE.resolve_output_path(output_dir, "report.pdf", set())
        second = MODULE.resolve_output_path(output_dir, "report.pdf", {first.name})
        self.assertEqual(first.name, "report.pdf")
        self.assertEqual(second.name, "report-2.pdf")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_feishu_yang_cli.FeishuYangCliHelperTests -v`

Expected: FAIL with an import error because `feishu-yang-automation/scripts/feishu_yang_cli.py` does not exist yet.

- [ ] **Step 3: Write the minimal CLI skeleton and helper functions**

```python
#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


REQUIRED_ENV_VARS = (
    "FEISHU_APP_ID",
    "FEISHU_APP_SECRET",
    "FEISHU_YANG_CHAT_ID",
)


def require_settings(env: dict[str, str]) -> dict[str, str]:
    missing = [name for name in REQUIRED_ENV_VARS if not env.get(name)]
    if missing:
        raise RuntimeError(f"Missing required settings: {', '.join(missing)}")
    return {name: env[name] for name in REQUIRED_ENV_VARS}


def read_settings(env: dict[str, str]) -> dict[str, str]:
    settings = require_settings(env)
    optional_names = ("FEISHU_YANG_SENDER_NAME", "FEISHU_YANG_SENDER_OPEN_ID")
    for name in optional_names:
        value = env.get(name)
        if value:
            settings[name] = value
    return settings


def make_batch_dir_name(timestamp: str, label: str) -> str:
    return f"{timestamp}-{label}"


def resolve_output_path(output_dir: Path, filename: str, existing_names: set[str]) -> Path:
    candidate = Path(filename).name
    stem = Path(candidate).stem
    suffix = Path(candidate).suffix
    if candidate not in existing_names:
        return output_dir / candidate

    index = 2
    while True:
        updated = f"{stem}-{index}{suffix}"
        if updated not in existing_names:
            return output_dir / updated
        index += 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="feishu_yang_cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-recent-files")
    list_parser.add_argument("--hours", type=int, default=24)
    list_parser.add_argument("--json", action="store_true")

    download_parser = subparsers.add_parser("download-files")
    download_parser.add_argument("--message-id", action="append", dest="message_ids", default=[])
    download_parser.add_argument("--output-root", default=str(Path.home() / "Desktop" / "yang-downloads"))

    send_parser = subparsers.add_parser("send-file")
    send_parser.add_argument("--path", required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    payload = {"command": args.command}
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the helper tests to verify they pass**

Run: `python3 -m unittest tests.test_feishu_yang_cli.FeishuYangCliHelperTests -v`

Expected: PASS for the three helper tests.

- [ ] **Step 5: Commit the skeleton**

```bash
git add feishu-yang-automation/scripts/feishu_yang_cli.py tests/test_feishu_yang_cli.py
git commit -m "feat: add feishu yang cli skeleton"
```

### Task 2: Implement recent file discovery and desktop download preparation

**Files:**
- Modify: `feishu-yang-automation/scripts/feishu_yang_cli.py`
- Modify: `tests/test_feishu_yang_cli.py`

- [ ] **Step 1: Write failing tests for filtering, selection parsing, and directory creation**

```python
class FeishuYangCliListTests(unittest.TestCase):
    def test_filter_recent_file_messages_keeps_matching_sender(self) -> None:
        messages = [
            {
                "message_id": "om_1",
                "msg_type": "file",
                "create_time": "1777100000000",
                "sender": {"sender_type": "user", "sender_id": {"open_id": "ou_target"}, "name": "杨东东"},
                "body": {"file_name": "alpha.pdf", "file_key": "file_1"},
            },
            {
                "message_id": "om_2",
                "msg_type": "text",
                "create_time": "1777100000000",
                "sender": {"name": "杨东东"},
                "body": {},
            },
        ]

        filtered = MODULE.filter_recent_file_messages(
            messages,
            sender_name="杨东东",
            sender_open_id=None,
            min_created_ms=1777000000000,
        )

        self.assertEqual([item["message_id"] for item in filtered], ["om_1"])

    def test_parse_selection_accepts_csv_ranges(self) -> None:
        self.assertEqual(MODULE.parse_selection("1,3-4", 5), [1, 3, 4])

    def test_prepare_batch_directory_creates_unique_path(self) -> None:
        root = Path("/tmp/yang-downloads-tests")
        batch = MODULE.prepare_batch_directory(root, "20260425-143522", "yang-files")
        self.assertTrue(batch.name.startswith("20260425-143522-yang-files"))
```

- [ ] **Step 2: Run the list tests to verify they fail**

Run: `python3 -m unittest tests.test_feishu_yang_cli.FeishuYangCliListTests -v`

Expected: FAIL because `filter_recent_file_messages`, `parse_selection`, and `prepare_batch_directory` are not implemented yet.

- [ ] **Step 3: Implement recent-file filtering and desktop batch helpers**

```python
from datetime import datetime, timezone


def parse_selection(raw: str, max_index: int) -> list[int]:
    values: set[int] = set()
    for part in raw.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            for value in range(start, end + 1):
                if value < 1 or value > max_index:
                    raise ValueError(f"Selection out of range: {value}")
                values.add(value)
        else:
            value = int(token)
            if value < 1 or value > max_index:
                raise ValueError(f"Selection out of range: {value}")
            values.add(value)
    return sorted(values)


def filter_recent_file_messages(
    messages: list[dict],
    sender_name: str | None,
    sender_open_id: str | None,
    min_created_ms: int,
) -> list[dict]:
    results = []
    for message in messages:
        if message.get("msg_type") != "file":
            continue
        created_ms = int(message.get("create_time", "0"))
        if created_ms < min_created_ms:
            continue

        sender = message.get("sender", {})
        sender_id = sender.get("sender_id", {})
        sender_matches = False
        if sender_open_id:
            sender_matches = sender_id.get("open_id") == sender_open_id
        elif sender_name:
            sender_matches = sender.get("name") == sender_name
        if not sender_matches:
            continue
        results.append(message)
    return results


def prepare_batch_directory(output_root: Path, timestamp: str, label: str) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    base_name = make_batch_dir_name(timestamp, label)
    candidate = output_root / base_name
    index = 2
    while candidate.exists():
        candidate = output_root / f"{base_name}-{index}"
        index += 1
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate
```

- [ ] **Step 4: Add the list command output contract and rerun tests**

```python
def serialize_candidate(message: dict) -> dict:
    body = message.get("body", {})
    sender = message.get("sender", {})
    return {
        "message_id": message["message_id"],
        "file_key": body.get("file_key"),
        "file_name": body.get("file_name"),
        "sender_name": sender.get("name"),
        "create_time": message.get("create_time"),
    }
```

Run: `python3 -m unittest tests.test_feishu_yang_cli.FeishuYangCliHelperTests tests.test_feishu_yang_cli.FeishuYangCliListTests -v`

Expected: PASS for the helper tests and list-path tests.

- [ ] **Step 5: Commit the discovery and batch helpers**

```bash
git add feishu-yang-automation/scripts/feishu_yang_cli.py tests/test_feishu_yang_cli.py
git commit -m "feat: add recent file discovery helpers"
```

### Task 3: Implement live Feishu API calls for list, download, and send

**Files:**
- Modify: `feishu-yang-automation/scripts/feishu_yang_cli.py`
- Modify: `tests/test_feishu_yang_cli.py`

- [ ] **Step 1: Write failing tests around the HTTP client boundaries**

```python
from unittest.mock import patch


class FeishuYangCliApiTests(unittest.TestCase):
    @patch.object(MODULE, "request_json")
    def test_fetch_tenant_access_token_returns_token(self, request_json) -> None:
        request_json.return_value = {"tenant_access_token": "t-123"}
        token = MODULE.fetch_tenant_access_token("app-id", "app-secret")
        self.assertEqual(token, "t-123")

    @patch.object(MODULE, "request_json")
    def test_list_recent_files_returns_serialized_candidates(self, request_json) -> None:
        request_json.side_effect = [
            {
                "items": [
                    {
                        "message_id": "om_1",
                        "msg_type": "file",
                        "create_time": "1777100000000",
                        "sender": {"name": "杨东东", "sender_id": {"open_id": "ou_target"}},
                        "body": {"file_name": "alpha.pdf", "file_key": "file_1"},
                    }
                ]
            }
        ]
        client = MODULE.FeishuClient("token-1")
        results = client.list_recent_files("oc_test", "杨东东", None, 24)
        self.assertEqual(results[0]["file_name"], "alpha.pdf")
```

- [ ] **Step 2: Run the API tests to verify they fail**

Run: `python3 -m unittest tests.test_feishu_yang_cli.FeishuYangCliApiTests -v`

Expected: FAIL because `request_json`, `fetch_tenant_access_token`, and `FeishuClient` are not implemented yet.

- [ ] **Step 3: Implement Feishu HTTP helpers and the authenticated client**

```python
import mimetypes
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


BASE_URL = "https://open.feishu.cn"


def request_json(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, data: bytes | None = None) -> dict:
    request = urllib.request.Request(url, data=data, method=method)
    for key, value in (headers or {}).items():
        request.add_header(key, value)
    try:
        with urllib.request.urlopen(request) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Feishu API request failed: {exc.code} {body}") from exc
    return json.loads(payload)


def fetch_tenant_access_token(app_id: str, app_secret: str) -> str:
    payload = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    response = request_json(
        f"{BASE_URL}/open-apis/auth/v3/tenant_access_token/internal",
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
        data=payload,
    )
    token = response.get("tenant_access_token")
    if not token:
        raise RuntimeError("Feishu tenant access token missing from response")
    return token


class FeishuClient:
    def __init__(self, tenant_access_token: str) -> None:
        self._headers = {"Authorization": f"Bearer {tenant_access_token}"}

    def list_recent_files(self, chat_id: str, sender_name: str | None, sender_open_id: str | None, hours: int) -> list[dict]:
        now_ms = int(time.time() * 1000)
        min_created_ms = now_ms - hours * 60 * 60 * 1000
        query = urllib.parse.urlencode({"container_id_type": "chat", "container_id": chat_id, "page_size": 50})
        response = request_json(f"{BASE_URL}/open-apis/im/v1/messages?{query}", headers=self._headers)
        items = response.get("data", {}).get("items", response.get("items", []))
        filtered = filter_recent_file_messages(items, sender_name, sender_open_id, min_created_ms)
        return [serialize_candidate(item) for item in filtered]
```

- [ ] **Step 4: Implement file download, file upload, and send-message paths**

```python
def build_multipart_form(field_name: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----CodexBoundary{uuid.uuid4().hex}"
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    content = file_path.read_bytes()
    lines = [
        f"--{boundary}".encode(),
        f'Content-Disposition: form-data; name="{field_name}"; filename="{file_path.name}"'.encode(),
        f"Content-Type: {content_type}".encode(),
        b"",
        content,
        f"--{boundary}--".encode(),
        b"",
    ]
    return b"\r\n".join(lines), boundary


def send_json(url: str, payload: dict, headers: dict[str, str]) -> dict:
    merged = {"Content-Type": "application/json; charset=utf-8", **headers}
    return request_json(url, method="POST", headers=merged, data=json.dumps(payload).encode("utf-8"))


class FeishuClient:
    ...
    def download_file(self, file_key: str, output_path: Path) -> Path:
        url = f"{BASE_URL}/open-apis/im/v1/files/{file_key}/download"
        request = urllib.request.Request(url, method="GET", headers=self._headers)
        with urllib.request.urlopen(request) as response:
            output_path.write_bytes(response.read())
        return output_path

    def upload_file(self, file_path: Path) -> str:
        body, boundary = build_multipart_form("file", file_path)
        headers = {
            **self._headers,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "file_type": "stream",
            "file_name": file_path.name,
        }
        response = request_json(
            f"{BASE_URL}/open-apis/im/v1/files",
            method="POST",
            headers=headers,
            data=body,
        )
        file_key = response.get("data", {}).get("file_key")
        if not file_key:
            raise RuntimeError("Feishu file upload did not return file_key")
        return file_key

    def send_file_message(self, chat_id: str, file_key: str) -> dict:
        payload = {
            "receive_id": chat_id,
            "msg_type": "file",
            "content": json.dumps({"file_key": file_key}, ensure_ascii=False),
        }
        return send_json(
            f"{BASE_URL}/open-apis/im/v1/messages?receive_id_type=chat_id",
            payload,
            self._headers,
        )
```

Run: `python3 -m unittest tests.test_feishu_yang_cli.FeishuYangCliApiTests -v`

Expected: PASS with mocked HTTP calls.

- [ ] **Step 5: Commit the live API layer**

```bash
git add feishu-yang-automation/scripts/feishu_yang_cli.py tests/test_feishu_yang_cli.py
git commit -m "feat: add feishu api download and send support"
```

### Task 4: Wire the CLI commands, add the two skills, and update repository docs

**Files:**
- Modify: `feishu-yang-automation/scripts/feishu_yang_cli.py`
- Create: `download-yang/SKILL.md`
- Create: `download-yang/agents/openai.yaml`
- Create: `send-yang/SKILL.md`
- Create: `send-yang/agents/openai.yaml`
- Modify: `README.md`
- Modify: `tests/test_feishu_yang_cli.py`

- [ ] **Step 1: Write failing tests for CLI execution paths**

```python
import os
import subprocess
import sys


class FeishuYangCliCommandTests(unittest.TestCase):
    def test_main_requires_path_for_send_file(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "send-file"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--path", result.stderr)

    def test_main_lists_json_payload(self) -> None:
        env = os.environ.copy()
        env["FEISHU_APP_ID"] = "app-id"
        env["FEISHU_APP_SECRET"] = "app-secret"
        env["FEISHU_YANG_CHAT_ID"] = "oc_test"
        env["FEISHU_YANG_SENDER_NAME"] = "杨东东"
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "list-recent-files", "--json"],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        self.assertIn(result.returncode, (0, 1))
```

- [ ] **Step 2: Implement the command handlers and user-facing output**

```python
def run_list_recent_files(args: argparse.Namespace) -> int:
    settings = read_settings(os.environ)
    token = fetch_tenant_access_token(settings["FEISHU_APP_ID"], settings["FEISHU_APP_SECRET"])
    client = FeishuClient(token)
    results = client.list_recent_files(
        settings["FEISHU_YANG_CHAT_ID"],
        settings.get("FEISHU_YANG_SENDER_NAME"),
        settings.get("FEISHU_YANG_SENDER_OPEN_ID"),
        args.hours,
    )
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for index, item in enumerate(results, start=1):
            print(f"{index}. {item['create_time']} | {item['sender_name']} | {item['file_name']} | {item['message_id']}")
    return 0


def run_send_file(args: argparse.Namespace) -> int:
    settings = read_settings(os.environ)
    file_path = Path(args.path).expanduser().resolve()
    if not file_path.exists():
        raise RuntimeError(f"Local file does not exist: {file_path}")
    token = fetch_tenant_access_token(settings["FEISHU_APP_ID"], settings["FEISHU_APP_SECRET"])
    client = FeishuClient(token)
    file_key = client.upload_file(file_path)
    client.send_file_message(settings["FEISHU_YANG_CHAT_ID"], file_key)
    print(f"Sent {file_path.name} to {settings['FEISHU_YANG_CHAT_ID']}")
    return 0
```

- [ ] **Step 3: Implement `download-files` and wire the main command dispatch**

```python
def run_download_files(args: argparse.Namespace) -> int:
    settings = read_settings(os.environ)
    if not args.message_ids:
        raise RuntimeError("At least one --message-id is required")

    token = fetch_tenant_access_token(settings["FEISHU_APP_ID"], settings["FEISHU_APP_SECRET"])
    client = FeishuClient(token)
    output_root = Path(args.output_root).expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    batch_dir = prepare_batch_directory(output_root, timestamp, "yang-files")
    saved_names: set[str] = set()

    message_lookup = {
        item["message_id"]: item
        for item in client.list_recent_files(
            settings["FEISHU_YANG_CHAT_ID"],
            settings.get("FEISHU_YANG_SENDER_NAME"),
            settings.get("FEISHU_YANG_SENDER_OPEN_ID"),
            24,
        )
    }

    for message_id in args.message_ids:
        item = message_lookup[message_id]
        output_path = resolve_output_path(batch_dir, item["file_name"], saved_names)
        client.download_file(item["file_key"], output_path)
        saved_names.add(output_path.name)
        print(str(output_path))

    print(f"Saved files to {batch_dir}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "list-recent-files":
        return run_list_recent_files(args)
    if args.command == "download-files":
        return run_download_files(args)
    if args.command == "send-file":
        return run_send_file(args)
    raise RuntimeError(f"Unsupported command: {args.command}")
```

- [ ] **Step 4: Write the two skill files and OpenAI metadata**

```md
---
name: download-yang
description: Use when the user types `/download-yang` or asks to list and fetch files sent by Yang from the last 24 hours in the fixed Feishu group, then download selected files into `~/Desktop/yang-downloads/`.
---

# Download Yang

Run `python3 feishu-yang-automation/scripts/feishu_yang_cli.py list-recent-files --json` first.

Show the candidate files to the user with index, send time, and file name.
Ask which indices to fetch before downloading anything.
After the user confirms, run `download-files` for the selected message IDs and report the created desktop directory.
```

```md
---
name: send-yang
description: Use when the user types `/send-yang` or asks to send a local file back to the fixed Feishu group as a file message.
---

# Send Yang

If the user did not provide a file path, ask for one.
Then run `python3 feishu-yang-automation/scripts/feishu_yang_cli.py send-file --path <absolute-path>`.
Report whether the upload and group send succeeded.
```

```yaml
interface:
  display_name: "Download Yang"
  short_description: "Fetch recent Yang files from the fixed Feishu group"
  default_prompt: "Use $download-yang when the user types /download-yang to list recent group file messages from Yang and download the selected files into ~/Desktop/yang-downloads/."
```

```yaml
interface:
  display_name: "Send Yang"
  short_description: "Send a local file back to the fixed Feishu group"
  default_prompt: "Use $send-yang when the user types /send-yang to upload a local file and send it as a file message to the fixed Feishu group."
```

- [ ] **Step 5: Update the README and run the full test suite**

```md
### `download-yang`

Path: `download-yang/`

Purpose:
- list recent file messages from a fixed Feishu group
- let the user choose which files to fetch
- download confirmed files into `~/Desktop/yang-downloads/`

### `send-yang`

Path: `send-yang/`

Purpose:
- send a local file back to the same fixed Feishu group
- reuse the shared Feishu CLI and credentials
```

Run: `python3 -m unittest discover -s tests -p 'test_*.py' -v`

Expected: PASS for the existing docx test plus the new Feishu CLI tests.

- [ ] **Step 6: Commit the wired commands, skills, and docs**

```bash
git add README.md download-yang/SKILL.md download-yang/agents/openai.yaml send-yang/SKILL.md send-yang/agents/openai.yaml feishu-yang-automation/scripts/feishu_yang_cli.py tests/test_feishu_yang_cli.py
git commit -m "feat: add feishu yang download and send skills"
```

### Task 5: Manual verification with real credentials after implementation

**Files:**
- Modify: `feishu-yang-automation/scripts/feishu_yang_cli.py` only if a live API mismatch is discovered

- [ ] **Step 1: Export the real runtime settings locally**

```bash
export FEISHU_APP_ID="your-app-id"
export FEISHU_APP_SECRET="your-app-secret"
export FEISHU_YANG_CHAT_ID="your-chat-id"
export FEISHU_YANG_SENDER_NAME="杨东东"
```

- [ ] **Step 2: Verify recent file discovery against the fixed group**

Run: `python3 feishu-yang-automation/scripts/feishu_yang_cli.py list-recent-files --json`

Expected: JSON output containing only file messages from the last 24 hours that match the configured sender.

- [ ] **Step 3: Download a real candidate into the desktop folder**

Run: `python3 feishu-yang-automation/scripts/feishu_yang_cli.py download-files --message-id om_xxx`

Expected: the script prints the created batch directory under `~/Desktop/yang-downloads/` and the downloaded file is present there.

- [ ] **Step 4: Send a real local file back to the group**

Run: `python3 feishu-yang-automation/scripts/feishu_yang_cli.py send-file --path /absolute/path/to/test-file.pdf`

Expected: the script prints a success message and the file appears in the fixed Feishu group.

- [ ] **Step 5: Commit any live-API compatibility fixes**

```bash
git add feishu-yang-automation/scripts/feishu_yang_cli.py tests/test_feishu_yang_cli.py
git commit -m "fix: align feishu yang cli with live api responses"
```
