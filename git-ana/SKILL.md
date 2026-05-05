---
name: git-ana
description: Use when the user enters /git-ana followed by a GitHub repository URL and wants a beginner-friendly technical analysis of the project, including its tech stack, architecture, key files, how the project works, and what learners can study from it.
---

# git-ana

Use this skill when the user types `/git-ana <GitHub repository URL>`.

Example:

```text
/git-ana https://github.com/owner/repo
```

## Goal

Analyze a GitHub project like a technical teacher. The output should help a beginner understand not only "what technologies are used", but also "why those technologies exist in the project" and "what knowledge can be learned from the project".

Default to a non-specialist explanation style: explain the project as if the reader can code a little but has not learned the project's domain. Translate technical claims into plain-language meaning before naming the formal term.

## Workflow

1. Parse and validate the GitHub URL.
   - Require exactly one GitHub repository URL.
   - Accept `https://github.com/<owner>/<repo>` and URLs with extra paths; normalize to the repository root.
   - If no URL is provided, ask the user for the repository URL.

2. Gather evidence from the repository.
   - Use current GitHub information; do not rely only on memory.
   - Inspect the repository root, README, package/build files, dependency manifests, config files, source directories, examples, docs, and tests when available.
   - Prefer primary project files over third-party summaries.
   - Useful files to inspect include:
     - `README*`, `docs/`, `examples/`
     - `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `vite.config.*`, `next.config.*`
     - `pyproject.toml`, `requirements.txt`, `uv.lock`, `setup.py`
     - `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`
     - `Dockerfile`, `docker-compose.yml`, `.github/workflows/`
     - `src/`, `app/`, `lib/`, `server/`, `client/`, `tests/`
   - If the repository is large, inspect representative files instead of reading everything.

3. Identify the project type and tech stack.
   - Determine what the project is for in one sentence.
   - Identify languages, frameworks, runtime, package manager, database/storage, UI framework, API style, build system, deployment/runtime, test tools, and CI if present.
   - Tie every claim to file evidence. Say "I infer" when a conclusion is not explicitly stated.

4. Explain the architecture for beginners.
   - Avoid jargon-first explanations.
   - Explain each important technology with:
     - what it does in this project
     - why the project likely uses it
     - what a learner should understand before modifying it
   - Use analogies only when they clarify the engineering idea.
   - Explain the project's likely request/data flow or execution flow.

5. Teach through key files.
   - Pick the most important files/directories.
   - For each one, explain:
     - role in the project
     - what to read first
     - what concept it teaches
   - Do not paste long source code. Summarize and link to files.

6. Produce a learning-oriented report in Chinese.
   - Use this structure:

```markdown
## 项目一句话

## 技术栈地图

## 小白版运行逻辑

## 关键目录和文件

## 背后的技术知识

## 学习路线

## 我会重点读哪里

## 不确定点

## 参考链接
```

7. Keep the report honest.
   - Do not claim technologies that were not found in repo evidence.
   - If a dependency appears in a manifest but usage was not inspected, say so.
   - If setup or architecture is unclear, list it under "不确定点".
   - Include links to the GitHub repository and important files inspected.

## Output Style

- Write in Chinese.
- Assume the reader can code a little but is new to the project's domain.
- Keep explanations non-professional and easy to understand: say "这个东西解决什么问题" before "它叫什么技术名".
- Avoid jargon-first wording. When a term is necessary, define it immediately in everyday language and then continue with the concrete project example.
- Be concrete and educational, not just a bullet list of dependencies.
- Explain acronyms and framework names the first time they appear.
- Prefer "这个项目里 X 负责..." over generic encyclopedia explanations.
- End with 3-5 practical learning tasks the user can do next.

## Safety and Scope

- Do not execute unknown project code during analysis.
- Do not run install scripts from an unfamiliar repository unless the user explicitly asks.
- Do not clone private repositories or access non-public content unless the user has provided access and asked for it.
- For security-sensitive projects, describe the design but avoid giving exploit instructions.
