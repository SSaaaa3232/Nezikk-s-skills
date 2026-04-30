---
name: nskill
description: Use when the user enters /nskill followed by a name to create and publish a same-named skill folder in the Nezikk-s-skills repository
---

# NSkill

Use this skill when the user types `/nskill <name>`, `/nskill "name"`, or `/nskill:"name"` and wants that name used as the target folder name in the `Nezikk-s-skills` repository.

## Workflow

1. Parse the text after `/nskill` as the target folder name.
   - Trim spaces and matching quotes, including ASCII quotes and Chinese quotes.
   - Treat the remaining text as the `目标文件夹名`.
   - Stop and ask for a valid name if it is empty, contains `/`, starts with `.`, or is `.` / `..`.
2. Work from the repository root named `Nezikk-s-skills`.
   - If the current directory is inside a worktree, use that worktree root.
   - If the current directory is elsewhere, locate or ask for the `Nezikk-s-skills` path before editing.
3. Create a folder whose name exactly matches the parsed target folder name.
   - Stop if that folder already exists, unless the user explicitly asks to update it.
   - Git cannot publish empty folders, so create a minimal `SKILL.md` inside the new folder.
4. Write the minimal `SKILL.md` template:

```markdown
---
name: <folder-name>
description: Use when the user asks to use the <folder-name> skill
---

# <folder-name>

Add the workflow for this skill here.
```

5. Verify the new skill folder.
   - Confirm `<folder-name>/SKILL.md` exists.
   - Confirm the frontmatter has `name` and `description`.
   - Run `git status --short`.
   - Run the repository test command if available, such as `python3 -m unittest discover -s tests -p 'test_*.py' -v`.
6. Publish the change after verification passes.
   - Run `git add <folder-name>/SKILL.md`.
   - Run `git commit -m "feat: add <folder-name> skill scaffold"`.
   - Run `git push`.
7. Report the created folder path, verification result, commit hash, and push result.

## Notes

- Do not create the target folder outside the `Nezikk-s-skills` repository.
- Do not overwrite existing files unless the user explicitly requests an update.
- If tests fail for reasons unrelated to the new folder, report the failure and do not push until the user confirms how to proceed.
