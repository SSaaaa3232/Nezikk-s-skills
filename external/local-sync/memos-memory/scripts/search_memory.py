#!/usr/bin/env python3
"""从 MemOS 搜索记忆"""

import argparse
import requests
import json
import os

MEMOS_API = os.environ.get("MEMOS_API", "http://localhost:8000")
SEARCH_ENDPOINT = f"{MEMOS_API}/product/search"

def search_memory(query: str, user_id: str, mem_cube_id: str = None, list_all: bool = False):
    """搜索记忆"""
    payload = {
        "query": query if query else "所有记忆",
        "user_id": user_id,
    }
    if mem_cube_id:
        payload["mem_cube_id"] = mem_cube_id

    headers = {"Content-Type": "application/json"}

    try:
        res = requests.post(SEARCH_ENDPOINT, headers=headers, data=json.dumps(payload), timeout=10)
        result = res.json()

        if "result" in result and result["result"]:
            print("找到的相关记忆:")
            print("-" * 50)
            for item in result["result"][:10]:  # 最多显示10条
                content = item.get("content", item.get("text", ""))
                print(f"- {content[:200]}...")
                if len(content) > 200:
                    print(f"  [完整内容 {len(content)} 字符]")
        else:
            print("未找到相关记忆")

        return result
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到 MemOS 服务 (http://localhost:8000)")
        print("请确保 MemOS 服务正在运行")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="从 MemOS 搜索记忆")
    parser.add_argument("--query", required=True, help="搜索查询")
    parser.add_argument("--user-id", required=True, help="用户 ID")
    parser.add_argument("--mem-cube-id", help="记忆立方体 ID (可选)")
    parser.add_argument("--list-all", action="store_true", help="列出所有记忆")

    args = parser.parse_args()
    search_memory(args.query, args.user_id, args.mem_cube_id, args.list_all)