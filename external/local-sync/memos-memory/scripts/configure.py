#!/usr/bin/env python3
"""配置 MemOS Skill"""

import argparse
import json
import os
from pathlib import Path

CONFIG_FILE = Path.home() / ".claude" / "skills" / "memos-memory" / "config.json"

def save_config(user_id: str, mem_cube_id: str = None, memos_api: str = None):
    """保存配置"""
    config = {
        "user_id": user_id,
        "mem_cube_id": mem_cube_id,
        "memos_api": memos_api or "http://localhost:8000"
    }

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    print(f"配置已保存到: {CONFIG_FILE}")
    print(f"用户 ID: {user_id}")
    if mem_cube_id:
        print(f"记忆立方体 ID: {mem_cube_id}")

def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return None

def main():
    parser = argparse.ArgumentParser(description="配置 MemOS Skill")
    parser.add_argument("--user-id", required=True, help="用户 ID (例如: claude-code-user)")
    parser.add_argument("--mem-cube-id", help="记忆立方体 ID (可选)")
    parser.add_argument("--memos-api", default="http://localhost:8000", help="MemOS API 地址")

    args = parser.parse_args()
    save_config(args.user_id, args.mem_cube_id, args.memos_api)

if __name__ == "__main__":
    main()