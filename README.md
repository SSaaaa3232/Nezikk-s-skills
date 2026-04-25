# Nezikk's Skills

Personal skill repository for Claude and Codex.

This repo stores reusable skills that can be copied into local skill directories and versioned in GitHub.

## Skills

### `synbio-academic-translator`

Path: `synbio-academic-translator/`

Purpose:
- translate Chinese academic text into polished English
- normalize terminology for synthetic biology, metabolic engineering, molecular biology, and microbial engineering
- support `.docx` manuscript input through automatic paragraph extraction

Key files:
- `synbio-academic-translator/SKILL.md`
- `synbio-academic-translator/references/terminology.md`
- `synbio-academic-translator/scripts/extract_docx_paragraphs.py`

### `docx-creater`

Path: `docx-creater/`

Purpose:
- create or export `.docx` documents from drafted content
- guide formatting confirmation before document generation
- support `/docx-create` as an explicit trigger

Key files:
- `docx-creater/SKILL.md`
- `docx-creater/agents/openai.yaml`

### `download-yang`

Path: `download-yang/`

Purpose:
- list recent Feishu file candidates from Yang through the shared CLI
- ask for index selection before downloading
- download only confirmed `message_id` values

Key files:
- `download-yang/SKILL.md`
- `download-yang/agents/openai.yaml`

### `send-yang`

Path: `send-yang/`

Purpose:
- ask for local file path when missing
- run shared CLI `send-file --path` to upload and send into Yang chat

Key files:
- `send-yang/SKILL.md`
- `send-yang/agents/openai.yaml`

### Shared Feishu CLI

Path: `feishu-yang-common/scripts/feishu_yang_cli.py`

Commands:
- `list-recent-files` (supports `--json`)
- `download-files` (accepts repeated `--message-id`, supports `--hours`)
- `send-file` (requires `--path`)

Environment variables:
- required: `FEISHU_APP_ID`, `FEISHU_APP_SECRET`, `FEISHU_YANG_CHAT_ID`
- optional: `FEISHU_YANG_SENDER_NAME`, `FEISHU_YANG_SENDER_OPEN_ID`, `FEISHU_API_BASE`, `FEISHU_HTTP_TIMEOUT`

## Tests

Current test coverage:
- `tests/test_extract_docx_paragraphs.py`
- `tests/test_feishu_yang_cli.py`

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Local Installation

### Quick Install With npm

If you use the `skills` CLI, you can install this repository directly from GitHub:

```bash
npx skills add SSaaaa3232/Nezikk-s-skills
```

Then copy or link the specific skill you want into your local skill directory if your runtime does not do that automatically.

### Manual Install

Typical local skill directories:

- Claude: `~/.claude/skills/`
- Codex: `~/.agents/skills/`

Example:

```bash
cp -R synbio-academic-translator ~/.claude/skills/
cp -R synbio-academic-translator ~/.agents/skills/
cp -R docx-creater ~/.claude/skills/
cp -R docx-creater ~/.agents/skills/
cp -R download-yang ~/.claude/skills/
cp -R download-yang ~/.agents/skills/
cp -R send-yang ~/.claude/skills/
cp -R send-yang ~/.agents/skills/
cp -R feishu-yang-common ~/.claude/skills/
cp -R feishu-yang-common ~/.agents/skills/
```

`download-yang` and `send-yang` depend on `feishu-yang-common/scripts/feishu_yang_cli.py`, so install/copy `feishu-yang-common` together with those two skills.
