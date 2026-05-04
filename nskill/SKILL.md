---
name: nskill
description: Use when the user enters /nskill followed by a skill name and optional function description to create, test, link, commit, and publish a complete same-named command skill in the Nezikk-s-skills repository. The skill name is also the folder name, frontmatter name, and slash command trigger.
---

# NSkill

Use this skill when the user types `/nskill <name> <function description>`, `/nskill <name>`, `/nskill "name" ...`, or `/nskill:"name" ...` and wants a new same-named command skill created in the `Nezikk-s-skills` repository.

Example:

```text
/nskill repeat 复述用户要求，便于同步用户想法和 agent 操作
```

This creates:

```text
repeat/                  # folder
repeat/SKILL.md          # skill file
name: repeat             # frontmatter name
/repeat                  # slash command trigger documented in the skill
```

## Goal

Turn one `/nskill <name> <function description>` request into a usable, tested, linked, committed, and pushed skill. Do not create an empty placeholder unless the user explicitly asks for a scaffold only.

## Workflow

1. Parse the text after `/nskill`.
   - Trim spaces and matching quotes, including ASCII quotes and Chinese quotes.
   - The first token is the `skill name`.
   - Everything after the first token is the `function description`.
   - Treat the `skill name` as the folder name, frontmatter `name`, and slash command trigger `/<skill-name>`.
   - Stop and ask for a valid name if the skill name is empty, contains `/`, starts with `.`, or is `.` / `..`.
   - Prefer lowercase kebab-case names. If the user gives spaces or unsafe characters in the name, ask for a safe command name instead of guessing.
   - If the function description is missing, ask for a one-sentence description unless the user explicitly requested scaffold-only creation.
2. Work from the repository root named `Nezikk-s-skills`.
   - If the current directory is inside a worktree, use that worktree root.
   - If the current directory is elsewhere, locate or ask for the `Nezikk-s-skills` path before editing.
3. Create a folder whose name exactly matches the parsed target folder name.
   - Stop if that folder already exists, unless the user explicitly asks to update it.
   - Git cannot publish empty folders, so create a complete `SKILL.md` inside the new folder.
4. Use `skill-creator` standards to write a complete `SKILL.md`.
   - The frontmatter `name` must equal `<skill-name>`.
   - The frontmatter `description` must clearly say when to use the skill, including the slash command `/<skill-name>`.
   - The body must document:
     - trigger format
     - examples
     - goal
     - workflow
     - output style or report shape when relevant
     - verification steps when relevant
     - boundaries and safety rules
   - The new skill must be directly usable when the user later types `/<skill-name> ...`.
   - Keep the skill concise. Add `references/`, `scripts/`, or `assets/` only if the function description truly needs them.

Required skeleton:

```markdown
---
name: <skill-name>
description: Use when the user enters /<skill-name> ... [specific trigger and function]
---

# <skill-name>

Use this skill when the user types `/<skill-name> ...`.

## Goal

[What this skill accomplishes.]

## Workflow

1. ...

## Output Style

...

## Boundaries

...
```

5. Add or update repository tests.
   - Create `tests/test_<skill_name_with_underscores>_skill.py`.
   - Test that the new `SKILL.md` contains:
     - `name: <skill-name>`
     - `/<skill-name>`
     - key words from the function description
     - `Workflow`
     - any important safety or verification rule
   - Test that `README.md` lists the new skill and links to `<skill-name>/SKILL.md`.
6. Update `README.md`.
   - Increase the Skills badge count.
   - Add the skill to the "My Skills" table.
   - Add a short card section under "Skills" explaining:
     - what it does
     - when to use it
     - what it will do
     - link to `SKILL.md`
7. Link the skill to Claude and Codex.
   - Run:

```bash
./scripts/link-skill.sh <skill-name>
```

   - Confirm:

```bash
readlink ~/.agents/skills/<skill-name>
readlink ~/.claude/skills/<skill-name>
```

8. Verify the new skill folder.
   - Confirm `<folder-name>/SKILL.md` exists.
   - Confirm the frontmatter has `name` and `description`.
   - Confirm `/<skill-name>` appears in the new skill body.
   - Run `git status --short`.
   - Run the focused test for the new skill.
   - Run the repository test command:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

9. Publish the change after verification passes.
   - Stage only files related to the new skill:

```bash
git add <skill-name>/SKILL.md tests/test_<skill_name_with_underscores>_skill.py README.md
```

   - Run `git commit -m "feat: add <skill-name> skill"`.
   - Run `git push`.
10. Report the created folder path, trigger command, verification result, symlink result, commit hash, and push result.

## Notes

- Do not create the target folder outside the `Nezikk-s-skills` repository.
- Do not overwrite existing files unless the user explicitly requests an update.
- If tests fail for reasons unrelated to the new folder, report the failure and do not push until the user confirms how to proceed.
- Do not create only a minimal placeholder when the user provided a function description. The point of `/nskill <name> <function>` is to generate a complete, usable skill.
- The skill name is a command. If the user says `/nskill repeat ...`, the final skill must be callable as `/repeat ...`.
- In general, a skill created from `/nskill <skill-name> ...` must be callable as `/<skill-name> ...`.
