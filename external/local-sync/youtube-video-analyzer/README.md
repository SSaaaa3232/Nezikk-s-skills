# YouTube Video Analyzer

A [Claude Code Skill](https://docs.anthropic.com/en/docs/claude-code) that analyzes YouTube videos — fetches transcripts, downloads comments, and generates structured analysis reports.

**Zero external dependencies.** Uses only Python standard library.

## Features

- Fetch video transcripts (multi-language, manual & auto-generated)
- Download comments (sorted by popular/recent, with limits)
- Full video analysis: transcript + comments + sentiment report
- Save transcripts as SRT / VTT / JSON
- Save comments as JSON
- Supports all YouTube URL formats (watch, short, embed, youtu.be)

## Installation

Copy this folder into your Claude Code skills directory:

```bash
# Project-level (recommended)
cp -r youtube-video-analyzer .claude/skills/

# Or user-level (available in all projects)
cp -r youtube-video-analyzer ~/.claude/skills/
```

No `pip install` needed. All scripts use only Python standard library (`urllib`, `json`, `xml`, `re`).

## Requirements

- Python 3.10+

## Usage

Once installed as a skill, Claude Code will automatically use it when you ask things like:

- "Summarize this YouTube video: https://www.youtube.com/watch?v=..."
- "Download the comments from this video"
- "What are people saying about this video?"
- "Get the Chinese subtitles for this video"
- "Analyze the sentiment of this video's comments"

### Direct Script Usage

```bash
# List available subtitle languages
python scripts/fetch_transcript.py <video> --list-languages

# Fetch transcript with timestamps
python scripts/fetch_transcript.py <video> en --timestamps

# Save transcript as SRT/VTT/JSON
python scripts/fetch_transcript.py <video> en --save --format srt

# Download top 500 comments
python scripts/fetch_comments.py <video> --limit 500 --sort popular

# Full analysis (transcript + comments)
python scripts/analyze_video.py <video> --lang en --comment-limit 500
```

`<video>` accepts video IDs (`dQw4w9WgXcQ`) or full URLs (`https://www.youtube.com/watch?v=...`).

## Project Structure

```
youtube-video-analyzer/
├── SKILL.md                    # Skill definition (read by Claude Code)
├── README.md
├── .gitignore
└── scripts/
    ├── youtube_api.py          # Zero-dependency YouTube API (transcript + comments)
    ├── utils.py                # Shared utilities
    ├── fetch_transcript.py     # Transcript fetcher CLI
    ├── fetch_comments.py       # Comment downloader CLI
    └── analyze_video.py        # Full analysis CLI
```

## How It Works

All YouTube data fetching is implemented in [`scripts/youtube_api.py`](scripts/youtube_api.py) using only Python standard library:

- **Transcripts**: Fetches the watch page HTML, extracts the InnerTube API key, calls `/youtubei/v1/player` to get caption track URLs, then parses the timedtext XML response.
- **Comments**: Extracts `ytcfg` and `ytInitialData` from the watch page, then paginates through comments via the `/youtubei/v1/next` InnerTube endpoint using continuation tokens.

No YouTube Data API key is required.

## License

MIT
