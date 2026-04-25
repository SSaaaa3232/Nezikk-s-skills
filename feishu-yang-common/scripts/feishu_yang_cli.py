#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_ENV_VARS = (
    "FEISHU_APP_ID",
    "FEISHU_APP_SECRET",
    "FEISHU_YANG_CHAT_ID",
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
