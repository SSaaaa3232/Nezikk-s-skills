#!/usr/bin/env python3
"""存储记忆到 MemOS"""

import argparse
import requests
import json
import os
from uuid import uuid4

MEMOS_API = os.environ.get("MEMOS_API", "http://localhost:8000")
ADD_ENDPOINT = f"{MEMOS_API}/product/add"

def store_memory(content: str, user_id: str, mem_cube_id: str = None):
    """存储记忆"""
    if not mem_cube_id:
        mem_cube_id = str(uuid4())

    payload = {
        "user_id": user_id,
        "mem_cube_id": mem_cube_id,
        "messages": [
            {"role": "user", "content": content}
        ],
        "async_mode": "sync"
    }

    headers = {"Content-Type": "application/json"}

    try:
        res = requests.post(ADD_ENDPOINT, headers=headers, data=json.dumps(payload), timeout=10)
        result = res.json()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到 MemOS 服务 (http://localhost:8000)")
        print("请确保 MemOS 服务正在运行")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="存储记忆到 MemOS")
    parser.add_argument("--content", required=True, help="要记忆的内容")
    parser.add_argument("--user-id", required=True, help="用户 ID")
    parser.add_argument("--mem-cube-id", help="记忆立方体 ID (可选)")

    args = parser.parse_args()
    store_memory(args.content, args.user_id, args.mem_cube_id)