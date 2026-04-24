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

## Tests

Current test coverage:
- `tests/test_extract_docx_paragraphs.py`

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
```
