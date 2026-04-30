#!/usr/bin/env python3
"""Shared utilities for YouTube Video Analyzer scripts."""

import re
import sys


def extract_video_id(url_or_id: str) -> str:
    """Extract 11-char YouTube video ID from various URL formats or raw ID."""
    patterns = [
        r"(?:v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be\/)([a-zA-Z0-9_-]{11})",
        r"(?:shorts\/)([a-zA-Z0-9_-]{11})",
        r"(?:embed\/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url_or_id):
        return url_or_id
    print(f"ERROR: Cannot extract video ID from: {url_or_id}", file=sys.stderr)
    sys.exit(1)


def seconds_to_hms(seconds: float) -> str:
    """Convert float seconds to HH:MM:SS,mmm (SRT standard)."""
    ms = int((seconds % 1) * 1000)
    s = int(seconds)
    h = s // 3600
    m = (s % 3600) // 60
    s = s % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
