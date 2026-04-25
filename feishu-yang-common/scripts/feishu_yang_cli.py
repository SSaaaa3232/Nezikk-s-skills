#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


REQUIRED_ENV_VARS = (
    "FEISHU_APP_ID",
    "FEISHU_APP_SECRET",
    "FEISHU_YANG_CHAT_ID",
)
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"
DEFAULT_HTTP_TIMEOUT = 30


def request_json(
    url: str,
    method: str = "GET",
    payload: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_HTTP_TIMEOUT,
) -> dict:
    request = urllib.request.Request(
        url=url,
        data=payload,
        headers=headers or {},
        method=method.upper(),
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
    decoded = raw.decode("utf-8")
    data = json.loads(decoded)
    if isinstance(data, dict):
        return data
    raise RuntimeError("Expected JSON object response")


def send_json(
    url: str,
    payload: dict,
    headers: dict[str, str],
    timeout: int = DEFAULT_HTTP_TIMEOUT,
) -> dict:
    request_headers = {"Content-Type": "application/json; charset=utf-8"}
    request_headers.update(headers)
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return request_json(
        url=url,
        method="POST",
        payload=body,
        headers=request_headers,
        timeout=timeout,
    )


def validate_feishu_response(response: dict, action: str) -> dict:
    code = response.get("code")
    if code is None:
        raise RuntimeError(f"{action} failed: missing Feishu response code")
    if code != 0:
        message = str(response.get("msg") or response.get("message") or "unknown error")
        raise RuntimeError(f"{action} failed: code={code}, msg={message}")
    return response


def fetch_tenant_access_token(app_id: str, app_secret: str) -> str:
    response = validate_feishu_response(
        send_json(
            f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal",
            {"app_id": app_id, "app_secret": app_secret},
            {},
        ),
        action="fetch tenant access token",
    )
    token = response.get("tenant_access_token")
    if not token:
        token = _as_dict(response.get("data")).get("tenant_access_token")
    if not token:
        raise RuntimeError("tenant_access_token is missing in response")
    return str(token)


def build_multipart_form(field_name: str, file_path: Path | str) -> tuple[str, bytes]:
    source_path = Path(file_path)
    filename = source_path.name
    file_bytes = source_path.read_bytes()
    boundary = f"----feishu-yang-{uuid.uuid4().hex}"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
    return f"multipart/form-data; boundary={boundary}", body


class FeishuClient:
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        api_base: str = FEISHU_API_BASE,
        timeout: int = DEFAULT_HTTP_TIMEOUT,
    ):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.tenant_access_token = fetch_tenant_access_token(app_id, app_secret)

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.tenant_access_token}"}

    def list_recent_files(
        self,
        chat_id: str,
        sender_name: str,
        sender_open_id: str,
        hours: int,
    ) -> list[dict]:
        min_created_ms = int((time.time() - (hours * 3600)) * 1000)
        page_token = ""
        all_items: list[dict] = []
        while True:
            params = {"container_id_type": "chat", "page_size": 50}
            if page_token:
                params["page_token"] = page_token
            query = urllib.parse.urlencode(params)
            url = f"{self.api_base}/im/v1/chats/{chat_id}/messages?{query}"
            response = validate_feishu_response(
                request_json(
                    url=url,
                    method="GET",
                    headers=self._auth_headers(),
                    timeout=self.timeout,
                ),
                action="list recent files",
            )
            data = _as_dict(response.get("data"))
            items = data.get("items", [])
            if isinstance(items, list):
                all_items.extend(items)
            has_more = bool(data.get("has_more"))
            next_page_token = data.get("page_token")
            if not has_more:
                break
            if not next_page_token:
                break
            page_token = str(next_page_token)
        return filter_recent_file_messages(all_items, sender_name, sender_open_id, min_created_ms)

    def download_file(self, file_key: str, output_path: Path | str) -> Path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"{self.api_base}/im/v1/files/{file_key}/download"
        request = urllib.request.Request(url=url, method="GET", headers=self._auth_headers())
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = response.read()
        target_path.write_bytes(payload)
        return target_path

    def upload_file(self, file_path: Path | str) -> str:
        source_path = Path(file_path)
        content_type, body = build_multipart_form("file", source_path)
        headers = self._auth_headers()
        headers["Content-Type"] = content_type
        response = request_json(
            url=f"{self.api_base}/im/v1/files",
            method="POST",
            payload=body,
            headers=headers,
            timeout=self.timeout,
        )
        validate_feishu_response(response, action="upload file")
        file_key = _as_dict(response.get("data")).get("file_key")
        if not file_key:
            raise RuntimeError("file_key is missing in upload response")
        return str(file_key)

    def send_file_message(self, chat_id: str, file_key: str) -> dict:
        payload = {
            "receive_id": chat_id,
            "msg_type": "file",
            "content": json.dumps({"file_key": file_key}, separators=(",", ":")),
        }
        return validate_feishu_response(
            send_json(
                f"{self.api_base}/im/v1/messages?receive_id_type=chat_id",
                payload,
                self._auth_headers(),
                timeout=self.timeout,
            ),
            action="send file message",
        )


def require_settings(env: dict[str, str]) -> dict[str, str]:
    missing = [name for name in REQUIRED_ENV_VARS if not env.get(name)]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required settings: {joined}")
    return {name: env[name] for name in REQUIRED_ENV_VARS}


def make_batch_dir_name(timestamp: str, label: str) -> str:
    return f"{timestamp}-{label}"


def _as_dict(value: object) -> dict:
    if isinstance(value, dict):
        return value
    return {}


def parse_selection(raw: str, max_index: int) -> list[int]:
    if max_index < 1:
        raise ValueError("max_index must be >= 1")

    values: list[int] = []
    seen: set[int] = set()
    for part in raw.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            left, right = token.split("-", 1)
            start = int(left.strip())
            end = int(right.strip())
            if start > end:
                raise ValueError(f"Invalid range: {token}")
            numbers = range(start, end + 1)
        else:
            numbers = [int(token)]
        for number in numbers:
            if number < 1 or number > max_index:
                raise ValueError(f"Selection out of range: {number}")
            if number not in seen:
                values.append(number)
                seen.add(number)
    return values


def filter_recent_file_messages(
    messages: list[dict],
    sender_name: str,
    sender_open_id: str,
    min_created_ms: int,
) -> list[dict]:
    filtered: list[dict] = []
    for message in messages:
        if message.get("message_type") != "file":
            continue
        sender = _as_dict(message.get("sender"))
        sender_id = _as_dict(sender.get("sender_id"))
        if sender_name and sender.get("sender_name") != sender_name:
            continue
        if sender_open_id and sender_id.get("open_id") != sender_open_id:
            continue
        try:
            created = int(message.get("create_time", 0))
        except (TypeError, ValueError):
            continue
        if created <= min_created_ms:
            continue
        filtered.append(message)
    return filtered


def prepare_batch_directory(output_root: Path, timestamp: str, label: str) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    base_name = make_batch_dir_name(timestamp, label)
    index = 1
    while True:
        if index == 1:
            name = base_name
        else:
            name = f"{base_name}-{index}"
        target = output_root / name
        try:
            target.mkdir(parents=False, exist_ok=False)
            return target
        except FileExistsError:
            index += 1


def serialize_candidate(message: dict) -> dict:
    body = _as_dict(message.get("body"))
    sender = _as_dict(message.get("sender"))
    return {
        "message_id": message.get("message_id"),
        "file_key": body.get("file_key"),
        "file_name": body.get("file_name"),
        "sender_name": sender.get("sender_name"),
        "create_time": message.get("create_time"),
    }


def resolve_output_path(output_dir: Path, filename: str, existing_names: set[str]) -> Path:
    candidate = Path(filename).name

    if candidate in {"", ".", ".."}:
        raise ValueError(f"Invalid filename: {filename!r}")

    def is_taken(name: str) -> bool:
        return name in existing_names or (output_dir / name).exists()

    if not is_taken(candidate):
        return output_dir / candidate

    source = Path(candidate)
    stem = source.stem
    suffix = source.suffix
    index = 2
    while True:
        updated = f"{stem}-{index}{suffix}"
        if not is_taken(updated):
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
    download_parser.add_argument(
        "--output-root", default=str(Path.home() / "Desktop" / "yang-downloads")
    )

    send_parser = subparsers.add_parser("send-file")
    send_parser.add_argument("--path", required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    print(json.dumps({"command": args.command}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
