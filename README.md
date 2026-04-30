# Nezikk's Skills

Personal skill repository for Claude and Codex.

This repo stores reusable skills that can be copied into local skill directories and versioned in GitHub.

## Skills

### `nskill`

Path: `nskill/`

Purpose:
- support `/nskill <name>` as a command-style trigger
- create a same-named skill folder in this repository
- verify the new folder and publish it with `git commit` and `git push`

Key files:
- `nskill/SKILL.md`

### `git-create`

Path: `git-create/`

Purpose:
- support `/git-create` as a command-style trigger
- confirm the local project folder and GitHub repository name
- create a private GitHub repository with `gh` and connect the local folder as its Git repository

Key files:
- `git-create/SKILL.md`

### `justdo`

Path: `justdo/`

Purpose:
- support `/justdo <文件夹名字>` as a command-style trigger
- create the requested folder under `/Users/saaaaa/Desktop/项目`
- avoid overwriting existing project folders

Key files:
- `justdo/SKILL.md`

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

### `feishu-yang/download-yang`

Path: `feishu-yang/download-yang/`

Purpose:
- list recent Feishu file candidates from Yang through the shared CLI
- ask for index selection before downloading
- download only confirmed `message_id` values

Key files:
- `feishu-yang/download-yang/SKILL.md`
- `feishu-yang/download-yang/agents/openai.yaml`

### `feishu-yang/send-yang`

Path: `feishu-yang/send-yang/`

Purpose:
- ask for local file path when missing
- run shared CLI `send-file --path` to upload and send into Yang chat

Key files:
- `feishu-yang/send-yang/SKILL.md`
- `feishu-yang/send-yang/agents/openai.yaml`

### Shared Feishu CLI

Path: `feishu-yang/feishu-yang-automation/scripts/feishu_yang_cli.py`

Commands:
- `list-recent-files` (supports `--json`)
- `download-files` (accepts repeated `--message-id`, supports `--hours`)
- `send-file` (requires `--path`)

Environment variables:
- required: `FEISHU_APP_ID`, `FEISHU_APP_SECRET`, `FEISHU_YANG_CHAT_ID`
- optional: `FEISHU_YANG_SENDER_NAME`, `FEISHU_YANG_SENDER_OPEN_ID`, `FEISHU_API_BASE`, `FEISHU_HTTP_TIMEOUT`

## Tests

Current test coverage:
- `tests/test_nskill_skill.py`
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
cp -R nskill ~/.claude/skills/
cp -R nskill ~/.agents/skills/
cp -R docx-creater ~/.claude/skills/
cp -R docx-creater ~/.agents/skills/
cp -R feishu-yang/download-yang ~/.claude/skills/
cp -R feishu-yang/download-yang ~/.agents/skills/
cp -R feishu-yang/send-yang ~/.claude/skills/
cp -R feishu-yang/send-yang ~/.agents/skills/
cp -R feishu-yang/feishu-yang-automation ~/.claude/skills/
cp -R feishu-yang/feishu-yang-automation ~/.agents/skills/
```

`download-yang` and `send-yang` depend on `feishu-yang/feishu-yang-automation/scripts/feishu_yang_cli.py`, so install/copy `feishu-yang-automation` together with those two skills.
