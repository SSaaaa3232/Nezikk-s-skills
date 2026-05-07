---
name: git-ana
description: Use when the user enters /git-ana with a GitHub URL or asks to analyze a project's build methodology, trace how the author built it from scratch, reverse-engineer architecture decisions, or dissect tech stack choices with evidence. Covers Chinese: 分析一下这个项目怎么构建的、作者是怎么从零搭建的、源码剖析、架构逆向、技术选型有什么依据、帮我剖析这个仓库、复现这个项目的构建思路、这个项目用了什么设计模式、作者为什么这么设计、项目架构分析
allowed-tools: Bash, Read, Write, Grep, Glob, WebFetch
model: sonnet
---

# git-ana

Use this skill when the user types `/git-ana <GitHub URL>` or asks in natural language to dissect a project's construction methodology. Typical triggers:

```text
/git-ana https://github.com/owner/repo

分析一下这个项目怎么构建的
作者是怎么从零搭建这个项目的 / 技术选型有什么依据
帮我剖析这个仓库的架构 / 这个项目用了什么设计模式
```

## Goal

Reverse-engineer the AUTHOR's build process. Given a GitHub URL, trace how the author constructed the project from scratch — what decisions they made, what evidence supports each inference, what methods and patterns they used. Output a methodology analysis document, not a beginner tutorial.

## Workflow

### Phase 1 — Project Origin & Scaffold Identification

1. Parse and validate the GitHub URL. Normalize to repo root.
2. Identify the project's starting point:
   - Scaffold/CLI traces: `create-next-app`, `npm init`, `vue create`, `cargo init`, fork markers
   - Evidence sources: `package.json` scripts field, git initial commit message, lockfile timestamps, config file defaults
   - Record as: **Origin** + evidence anchor + confidence (HIGH/MEDIUM/LOW)

### Phase 2 — Tech Stack Decision Tree

1. Gather evidence from: README, package/build files, dependency manifests, config files, source directories.
2. For each major technology choice, answer:
   - What was chosen?
   - What were the alternatives?
   - Why did the author likely pick this? (cite evidence: type constraints, performance needs, ecosystem lock-in)
3. Format as a decision table:

```
| Problem | Options | Choice | Evidence | Inference |
|---------|---------|--------|----------|------------|
| ...     | ...     | ...    | ...      | ...        |
```

### Phase 3 — Architecture Construction Timeline

1. From commit history and directory structure, infer the BUILD ORDER.
2. Key questions:
   - What was built first? (auth? data model? UI shell? routing?)
   - What was added later? (tests? CI/CD? monitoring? docs?)
   - Where are the "get it working → make it right" pivot points?
3. Output as a chronological timeline, each step with evidence.

### Phase 4 — Key Implementation Analysis

1. Identify 3-5 core modules/flows (auth, data pipeline, API design, state management, etc.)
2. For each one, analyze:
   - **Pattern used** (middleware chain, factory, observer, repository, etc.)
   - **Author's approach** (unusual or idiomatic? why this pattern for this problem?)
   - **Evidence** (file:line patterns, commit messages, config structure)
3. Do NOT explain what the code does. State what pattern the author chose, where, and why that reveals their intent.

### Phase 5 — Evidence Table

Output a unified evidence table:

```
| # | Discovery | Evidence Anchor | Confidence |
|---|-----------|-----------------|------------|
| 1 | ...       | file:line / commit hash / config key | HIGH/MEDIUM/LOW |
```

Confidence standard:
- **HIGH**: Directly visible in source + cross-referenced (e.g., config + code usage both confirm)
- **MEDIUM**: Inferred from patterns or single-source, not cross-validated
- **LOW**: Guess based on conventions or naming alone

### Phase 6 — FACTS / INFERENCES / UNKNOWNS

Categorize all findings:

- **FACTS**: Directly confirmed in code or configuration — no interpretation needed
- **INFERENCES**: Reasonable deductions from evidence, with explicit reasoning chain
- **UNKNOWNS**: Gaps where the author's intent is unclear or evidence is missing

### Phase 7 — Reproduction Path

If someone wanted to rebuild this project from scratch with the same methodology:
1. Step-by-step reconstruction order
2. What to build at each step and why
3. What the author's approach teaches about the problem domain

## Output Structure

```markdown
## 项目一句话 + 方法论总结

## 技术选型决策树
（Problem → Options → Choice → Evidence → Inference 表格）

## 架构构建推演
（时间线：作者从哪开始，一步步加了什么，每一步的证据是什么）

## 关键实现分析
（3-5 个核心模块：模式选择 + 作者思路 + 证据锚点）

## 证据表
（发现 + 证据锚点 + 置信度，至少 5 条）

## FACTS / INFERENCES / UNKNOWNS

## 复现路径
（如果我想重写一个，具体该怎么做）

## 不确定点

## 参考链接
（GitHub 仓库链接、关键文件链接等）
```

## Output Style

- Write in Chinese (code identifiers and file paths in English).
- Every claim must be anchored to evidence: file path, line pattern, commit hash, or config key.
- Confidence levels must be explicit on every claim.
- Do NOT explain what the code does — state what was found, where, and why it reveals the author's intent.
- Prefer "作者这里选了 X 而不是 Y，依据是 Z" over "这个项目用了 X".

## Verification

After completing the analysis:
1. The evidence table has ≥5 entries, each with a verifiable evidence anchor.
2. Every INFERENCE has a stated chain of reasoning.
3. The reproduction path is concrete and actionable (specific steps, not abstract advice).
4. The report cleanly separates FACTS (confirmed) from INFERENCES (deduced).

## Boundaries

- Do not execute unknown project code during analysis.
- Do not run install scripts from an unfamiliar repository unless the user explicitly asks.
- Do not clone private repositories or access non-public content without authorization.
- For security-sensitive projects, describe design but avoid exploit instructions.
- This skill analyzes methodology — it does NOT audit code quality, review PRs, or judge the author's skill level.
