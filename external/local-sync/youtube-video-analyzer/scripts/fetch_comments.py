#!/usr/bin/env python3
"""
YouTube Comment Downloader
Usage:
  python fetch_comments.py <video_id_or_url> [--limit N] [--sort popular|recent] [--save]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from utils import extract_video_id
from youtube_api import download_comments as _download, SORT_BY_POPULAR, SORT_BY_RECENT


def parse_votes(vote_str: str) -> int:
    vote_str = str(vote_str).strip().replace(",", "")
    try:
        if vote_str.endswith("K"):
            return int(float(vote_str[:-1]) * 1_000)
        if vote_str.endswith("M"):
            return int(float(vote_str[:-1]) * 1_000_000)
        return int(vote_str)
    except (ValueError, AttributeError):
        return 0


def download_comments_cli(video_id: str, limit: int = None, sort: str = "popular", save: bool = False):
    sort_by = SORT_BY_POPULAR if sort == "popular" else SORT_BY_RECENT

    print(f"Downloading comments for {video_id} (sort={sort}, limit={limit or 'all'})...", file=sys.stderr)

    comments = []
    for i, comment in enumerate(_download(video_id, sort_by=sort_by, limit=limit)):
        comment["votes_int"] = parse_votes(comment.get("votes", 0))
        comments.append(comment)
        if (i + 1) % 100 == 0:
            print(f"  Downloaded {i + 1} comments...", file=sys.stderr)

    print(f"Total comments downloaded: {len(comments)}", file=sys.stderr)

    top_comments = sorted(comments, key=lambda c: c["votes_int"], reverse=True)[:10]

    output = {
        "video_id": video_id,
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
        "total_downloaded": len(comments),
        "sort_order": sort,
        "top_comments": [
            {
                "author": c.get("author", ""),
                "text": c.get("text", ""),
                "votes": c.get("votes", "0"),
                "votes_int": c["votes_int"],
                "time": c.get("time", ""),
                "heart": c.get("heart", False),
                "reply": c.get("reply", False),
            }
            for c in top_comments
        ],
        "all_comments": [
            {
                "cid": c.get("cid", ""),
                "author": c.get("author", ""),
                "text": c.get("text", ""),
                "votes": c.get("votes", "0"),
                "votes_int": c["votes_int"],
                "time": c.get("time", ""),
                "heart": c.get("heart", False),
                "reply": c.get("reply", False),
            }
            for c in comments
        ],
    }

    sep = "=" * 60
    print(f"\n{sep}")
    print(f"TOP 10 COMMENTS (by votes)")
    print(f"{sep}")
    for idx, c in enumerate(output["top_comments"], 1):
        heart = "[heart] " if c["heart"] else ""
        print(f"\n#{idx:02d} [{c['votes']} votes] {heart}{c['author']} - {c['time']}")
        print(f"    {c['text'][:200]}{'...' if len(c['text']) > 200 else ''}")

    print(f"\n{sep}")
    print(f"SAMPLE: First 20 recent comments")
    print(f"{sep}")
    for idx, c in enumerate(output["all_comments"][:20], 1):
        print(f"\n#{idx:02d} [{c['votes']} votes] {c['author']} - {c['time']}")
        print(f"    {c['text'][:200]}{'...' if len(c['text']) > 200 else ''}")

    if save:
        filename = f"{video_id}_comments.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\nAll comments saved to: {filename}", file=sys.stderr)

    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    video_input = sys.argv[1]
    video_id = extract_video_id(video_input)
    args = sys.argv[2:]

    limit = None
    if "--limit" in args:
        idx = args.index("--limit")
        try:
            limit = int(args[idx + 1])
        except (IndexError, ValueError):
            print("ERROR: --limit requires a number", file=sys.stderr)
            sys.exit(1)

    sort = "popular"
    if "--sort" in args:
        idx = args.index("--sort")
        try:
            sort = args[idx + 1]
        except IndexError:
            pass

    save = "--save" in args
    download_comments_cli(video_id, limit=limit, sort=sort, save=save)
