---
name: youtube-video-analyzer
description: "Analyze YouTube videos: fetch transcripts, download comments, generate summaries, sentiment analysis, and audience insights. Use when asked to summarize, analyze, review sentiment, download subtitles, or download comments for any YouTube video."
---

# YouTube Video Analyzer Skill

## Setup

No external dependencies required. All scripts use only Python standard library.

---

## Available Scripts

All scripts are located in the `scripts/` subdirectory.

| Script | Purpose |
|--------|---------|
| `scripts/fetch_transcript.py` | Download video transcripts (multi-language, timestamped, save to file) |
| `scripts/fetch_comments.py` | Download all video comments (limit, sort, save to file) |
| `scripts/analyze_video.py` | All-in-one analysis (transcript + comments + sentiment report) |
| `scripts/youtube_api.py` | Zero-dependency YouTube API module (transcript + comments) |
| `scripts/utils.py` | Shared utilities (video ID extraction, time formatting) |

---

## Task Routing

Based on what the user asks, choose the appropriate action:

| User Intent | Action |
|-------------|--------|
| Summarize / analyze video content | Run `scripts/analyze_video.py <video>` |
| Content summary only (no comments) | Run `scripts/analyze_video.py <video> --mode transcript-only` |
| Sentiment / comment analysis only | Run `scripts/analyze_video.py <video> --mode comments-only` |
| Download subtitle file | Run `scripts/fetch_transcript.py <video> [language] --save` |
| Download subtitle in specific format | Run `scripts/fetch_transcript.py <video> [language] --save --format srt\|vtt\|json` |
| Download comments file | Run `scripts/fetch_comments.py <video> --save` |
| List available subtitle languages | Run `scripts/fetch_transcript.py <video> --list-languages` |

---

## Script Usage

### scripts/fetch_transcript.py

```bash
# Fetch transcript (print to terminal)
python scripts/fetch_transcript.py <video_id_or_url> [language]

# List all available subtitle languages
python scripts/fetch_transcript.py <video_id_or_url> --list-languages

# Save transcript to file (default: SRT format)
python scripts/fetch_transcript.py <video_id_or_url> [language] --save

# Save in specific format (srt, vtt, or json)
python scripts/fetch_transcript.py <video_id_or_url> [language] --save --format vtt

# Output with timestamps
python scripts/fetch_transcript.py <video_id_or_url> [language] --timestamps

# Examples
python scripts/fetch_transcript.py dQw4w9WgXcQ zh-Hans --save
python scripts/fetch_transcript.py dQw4w9WgXcQ en --save --format json
python scripts/fetch_transcript.py https://www.youtube.com/watch?v=dQw4w9WgXcQ en --timestamps
```

### scripts/fetch_comments.py

```bash
# Download comments (print summary to terminal)
python scripts/fetch_comments.py <video_id_or_url>

# Save all comments to JSON file (output: <video_id>_comments.json)
python scripts/fetch_comments.py <video_id_or_url> --save

# Limit number of comments
python scripts/fetch_comments.py <video_id_or_url> --limit 500

# Sort by popularity (default: recent)
python scripts/fetch_comments.py <video_id_or_url> --sort popular

# Combined example
python scripts/fetch_comments.py dQw4w9WgXcQ --limit 1000 --sort popular --save
```

### scripts/analyze_video.py

```bash
# Full analysis (transcript + comments + sentiment)
python scripts/analyze_video.py <video_id_or_url>

# Content analysis only (skip comments)
python scripts/analyze_video.py <video_id_or_url> --mode transcript-only

# Comment sentiment analysis only (skip transcript)
python scripts/analyze_video.py <video_id_or_url> --mode comments-only

# Specify subtitle language (use zh-Hans for Simplified Chinese videos)
python scripts/analyze_video.py <video_id_or_url> --lang zh-Hans

# Limit number of comments to analyze (default: 500)
python scripts/analyze_video.py <video_id_or_url> --comment-limit 1000

# Save all raw data to JSON
python scripts/analyze_video.py <video_id_or_url> --save
```

---

## Output Analysis Format

After running the scripts, produce the following structured report **in the user's language**:

### 1. Video Overview
- Video ID and URL
- Transcript language and source (manual / auto-generated)
- Total comments (downloaded count)

### 2. Content Summary
(Based on transcript, 150-250 words)

### 3. Key Takeaways
(3-7 bullet points)

### 4. Important Timestamps
(Only when transcript includes timestamps)

### 5. Sentiment Analysis

#### Overall Sentiment
- Positive: XX%
- Neutral: XX%
- Negative: XX%

#### Top Comments (Top 3-5 by votes)
List the most-upvoted comments (original text + vote count)

#### Major Audience Feedback Themes
Summarize recurring themes from the comments

#### Controversies or Negative Feedback (if any)

### 6. Audience Profile

---

## Error Handling

| Error | Resolution |
|-------|------------|
| Transcript unavailable | Inform user, proceed with comment download and sentiment analysis |
| Comments disabled | Inform user, proceed with transcript and content analysis |
| Video unavailable | Report error, suggest checking URL or region restrictions |
| Subtitle language not found | Run `--list-languages` and prompt user to select |
| Network timeout | Suggest retry, or reduce comment limit (`--limit`) |

---

## Notes
- No external dependencies or API keys required
- Full comment download can be slow; use `--limit 500` for a quick preview first
- Sentiment analysis is based on the Agent's semantic understanding of comment text; no additional NLP libraries needed
- Chinese video subtitles: Simplified `zh-Hans`, Traditional `zh-Hant`
- Place this folder in `.github/skills/` or `.claude/skills/` directory to activate
