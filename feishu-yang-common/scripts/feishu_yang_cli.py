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


def resolve_output_path(output_dir: Path, filename: str, existing_names: set[str]) -> Path:
    candidate = Path(filename).name
    if candidate not in existing_names:
        return output_dir / candidate

    source = Path(candidate)
    stem = source.stem
    suffix = source.suffix
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
