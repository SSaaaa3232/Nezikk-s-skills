---
name: repeat
description: Use when the user enters /repeat followed by a request or idea and wants the agent to restate the requirement clearly, align the user's intent with the agent's planned operation, and surface goals, constraints, assumptions, and next steps before execution.
---

# repeat

Use this skill when the user types `/repeat` followed by something they want restated or clarified.

Example:

```text
/repeat 帮我创建一个分析 GitHub 项目技术栈的 skill，要适合小白学习
```

## Goal

Restate the user's request in a clear, structured way so the user and agent share the same understanding before work begins. This skill is for alignment, not execution.

## Workflow

1. Parse the content after `/repeat`.
   - If no content is provided, ask the user what they want restated.
   - Preserve important names, paths, commands, URLs, file names, and constraints exactly.
   - Do not add new requirements that the user did not imply.

2. Identify the user's intent.
   - What outcome does the user want?
   - What should the agent do?
   - What should the agent avoid?
   - What context or prior decision matters?

3. Restate the requirement.
   - Use concise Chinese.
   - Prefer concrete, checkable wording.
   - Separate confirmed facts from assumptions.
   - If the request implies an implementation workflow, describe the likely next actions without starting them.

4. Surface ambiguity.
   - If the request has unclear scope, list the ambiguity.
   - Ask at most 1-3 targeted questions only when the ambiguity blocks correct execution.
   - If a reasonable default is obvious, state the default instead of asking.

5. Stop after the restatement.
   - Do not edit files, run commands, browse, commit, or execute the requested task unless the user explicitly asks to continue after the repeat.

## Output Style

Use this structure:

```markdown
你的意思是：
[one clear paragraph]

我理解要做的是：
- ...
- ...

关键约束：
- ...

我会默认这样处理：
- ...

需要你确认的点：
- ...
```

Omit sections that do not apply. Keep the response short enough that the user can quickly confirm or correct it.

## Boundaries

- Do not execute the repeated request.
- Do not silently transform the user's goal into a different task.
- Do not over-explain simple requests.
- Do not ask questions when the user's intent is already clear.
- Do not record the repeated content into memory or files unless another skill explicitly handles that.
