# SKILL.md Skeleton

Use this template when generating a new skill via nskill. Fill in `<>` placeholders.

```markdown
---
name: <skill-name>
description: Use when the user enters /<skill-name> ... [add 8-15 natural-language trigger phrases the user would actually say, covering both slash commands and conversational requests]
allowed-tools: Bash, Read, Write, Grep
model: sonnet
---

# <skill-name>

Use this skill when the user types `/<skill-name> ...` or asks in natural language to <task description>.

## Goal

<One sentence: what this skill accomplishes>

## Workflow

1. <Step 1>
2. <Step 2>
...

## Output Style

<Format expectations: language, structure, tone>

## Verification

After completing the task:
1. <Check 1>
2. <Check 2>
...

## Boundaries

- <Safety rule 1>
- <Safety rule 2>
...
```

## Frontmatter Field Rules

### name
Lowercase kebab-case. Must match folder name and slash command.

### description
- First sentence: "Use when the user enters `/<name>` ..." (required)
- Then: list 8-15 natural language trigger phrases covering:
  - Slash commands: `/<name> <args>`
  - Conversational: task-related natural language queries
  - Variants: different ways users express the same intent
- Include Chinese phrases if the target user speaks Chinese
- Keep under ~500 characters total for context efficiency

### allowed-tools

Follow the principle of least privilege:

| Task Type | Tools |
|-----------|-------|
| Read-only analysis | Read, Grep |
| Read + report generation | Read, Grep, Write |
| Read + modify files | Read, Grep, Write, Edit |
| Execute commands/scripts | Read, Grep, Write, Bash |
| Web content retrieval | + WebFetch |
| Image generation | + ImageGenerate |

**Never give `Agent` tool unless the user explicitly requests multi-agent orchestration.**

### model

Match task difficulty to model capability:

| model | Best For | Example Tasks |
|-------|----------|---------------|
| `opus` | Heavy reasoning, code analysis, complex chains | Reverse engineering, architecture design, multi-step debug |
| `sonnet` | Structured output, balanced speed/quality | Report generation, doc writing, code review |
| `haiku` | Simple lookups, fast classifiers | Keyword check, file existence, format validation |

## Body Section Rules

### Workflow
- Use numbered steps (1, 2, 3...)
- Each step: clear action verb + what to check
- Include exact bash commands or search patterns when relevant
- Don't assume tool availability — check what allowed-tools permits

### Output Style
- Specify language (Chinese/English)
- Specify structure (table/markdown/code)
- Specify tone (educational/technical/concise)

### Boundaries
- What this skill MUST NOT do
- Safety constraints (no destructive actions, educational use only, etc.)
- Rate limiting and respect for target systems

### References / Scripts / Assets

Only include if needed. If SKILL.md exceeds 500 lines:
1. Long docs → references/
2. Stable operations → scripts/
3. Templates/samples → assets/
