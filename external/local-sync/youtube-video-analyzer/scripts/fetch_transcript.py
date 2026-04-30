#!/usr/bin/env python3
"""
YouTube Transcript Fetcher
Usage:
  python fetch_transcript.py <video_id_or_url> [language] [options]

Options:
  --save                Save transcript to file (default: .srt format)
  --format srt|vtt|json Save format, default: srt
  --timestamps          Print timestamped text to terminal (for analysis)
  --list-languages      List all available subtitle languages

Examples:
  python fetch_transcript.py dQw4w9WgXcQ en --save
  python fetch_transcript.py dQw4w9WgXcQ zh-Hans --save --format srt
  python fetch_transcript.py dQw4w9WgXcQ en --timestamps
  python fetch_transcript.py dQw4w9WgXcQ --list-languages
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from utils import extract_video_id, seconds_to_hms
from youtube_api import list_transcripts, find_transcript


def list_languages(video_id: str):
    manual, generated, trans_langs = list_transcripts(video_id)

    print(f"\nFor this video ({video_id}) transcripts are available:\n")
    if manual:
        print("(MANUALLY CREATED)")
        for t in manual:
            print(f" - {t.language_code} (\"{t.language}\")")
    if generated:
        print("\n(GENERATED)")
        for t in generated:
            print(f" - {t.language_code} (\"{t.language}\")")
    if trans_langs:
        print("\n(TRANSLATION LANGUAGES)")
        for name, code in trans_langs:
            print(f" - {code} (\"{name}\")")


def _format_srt(entries):
    """Format transcript entries as SRT subtitle format."""
    lines = []
    for i, e in enumerate(entries, 1):
        start = seconds_to_hms(e.start)
        end = seconds_to_hms(e.start + e.duration)
        lines.append(f"{i}")
        lines.append(f"{start} --> {end}")
        lines.append(e.text)
        lines.append("")
    return "\n".join(lines)


def _format_vtt(entries):
    """Format transcript entries as WebVTT subtitle format."""
    lines = ["WEBVTT", ""]
    for e in entries:
        start = seconds_to_hms(e.start).replace(",", ".")
        end = seconds_to_hms(e.start + e.duration).replace(",", ".")
        lines.append(f"{start} --> {end}")
        lines.append(e.text)
        lines.append("")
    return "\n".join(lines)


def fetch(
    video_id: str,
    language: str = "en",
    save: bool = False,
    fmt: str = "srt",
    timestamps: bool = False,
):
    priority = list(dict.fromkeys([language, "en"]))
    transcript = find_transcript(video_id, priority)
    entries = transcript.fetch()
    lang_code = transcript.language_code
    source = "auto-generated" if transcript.is_generated else "manual"

    if timestamps:
        print(f"# Video: https://www.youtube.com/watch?v={video_id}")
        print(f"# Language: {transcript.language} ({lang_code}) [{source}]")
        print(f"# Snippets: {len(entries)}\n")
        for e in entries:
            ts = seconds_to_hms(e.start).replace(",", ".")
            print(f"[{ts}] {e.text}")
    else:
        print(" ".join(e.text for e in entries))

    if save:
        if fmt == "srt":
            content = _format_srt(entries)
            filename = f"{video_id}_transcript_{lang_code}.srt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

        elif fmt == "vtt":
            content = _format_vtt(entries)
            filename = f"{video_id}_transcript_{lang_code}.vtt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

        elif fmt == "json":
            output = {
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "language": transcript.language,
                "language_code": lang_code,
                "is_generated": transcript.is_generated,
                "total_snippets": len(entries),
                "plain_text": " ".join(e.text for e in entries),
                "timestamped": [
                    {
                        "timestamp": seconds_to_hms(e.start),
                        "start": round(e.start, 3),
                        "duration": round(e.duration, 3),
                        "end": round(e.start + e.duration, 3),
                        "text": e.text,
                    }
                    for e in entries
                ],
            }
            filename = f"{video_id}_transcript_{lang_code}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
        else:
            print(f"ERROR: Unknown format '{fmt}'. Use srt, vtt, or json.", file=sys.stderr)
            sys.exit(1)

        print(f"\nTranscript saved to: {filename}", file=sys.stderr)
        print(f"   Format   : {fmt.upper()}", file=sys.stderr)
        print(f"   Language : {transcript.language} ({lang_code}) [{source}]", file=sys.stderr)
        print(f"   Snippets : {len(entries)}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    video_input = sys.argv[1]
    video_id = extract_video_id(video_input)
    args = sys.argv[2:]

    if "--list-languages" in args:
        list_languages(video_id)
    else:
        language = next((a for a in args if not a.startswith("--")), "en")
        save = "--save" in args
        timestamps = "--timestamps" in args

        fmt = "srt"
        if "--format" in args:
            idx = args.index("--format")
            fmt = args[idx + 1] if idx + 1 < len(args) else "srt"

        fetch(video_id, language, save, fmt, timestamps)
