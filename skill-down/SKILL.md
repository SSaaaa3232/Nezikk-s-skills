---
name: skill-down
description: Use when the user enters /skill-down followed by an npx skills add command or GitHub skill repository URL, to import the skill into the Nezikk-s-skills repository, record its source, and link it to both Codex and Claude.
---

# Skill Down

Use this skill when the user types `/skill-down` followed by a command like:

```bash
/skill-down npx skills add https://github.com/op7418/guizang-ppt-skill --skill guizang-ppt-skill
```

The goal is not to install directly into one runtime. The goal is to store the external skill in this repository, record where it came from, then link the same stored skill to both Codex and Claude.

## Workflow

1. Locate the `Nezikk-s-skills` repository root.

2. Parse the text after `/skill-down`.
   - Accept the full `npx skills add <repo-url> --skill <skill-name>` form.
   - Also accept `<repo-url> --skill <skill-name>`.
   - Require `--skill`.

3. Run the repository importer:

```bash
python3 scripts/import_external_skill.py "npx skills add https://github.com/op7418/guizang-ppt-skill --skill guizang-ppt-skill"
```

4. The importer will:
   - clone the GitHub repository into a temporary directory
   - find the requested skill directory by `SKILL.md`
   - copy it into `external/<github-owner>/<repo-name>/<skill-name>/`
   - write `external/<github-owner>/<repo-name>/SOURCE.md`
   - link the imported skill to `~/.agents/skills/<skill-name>`
   - link the imported skill to `~/.claude/skills/<skill-name>`

5. If the external skill was already imported, stop and report the existing path.
   - Only use `--replace` when the user explicitly asks to overwrite the local external copy.

6. Verify after import:

```bash
test -f external/<github-owner>/<repo-name>/<skill-name>/SKILL.md
test -f external/<github-owner>/<repo-name>/SOURCE.md
test -L "$HOME/.agents/skills/<skill-name>"
test -L "$HOME/.claude/skills/<skill-name>"
```

7. Commit and push the imported skill unless the user explicitly says not to:

```bash
git add external/<github-owner>/<repo-name> README.md
git commit -m "feat: import <skill-name> skill"
git push
```

## Notes

- Do not copy the same external skill separately into Claude and Codex directories.
- The canonical copy is the one inside this repository.
- Keep `SOURCE.md` accurate so the original author, repository, commit, license, and local modifications are traceable.
- If the link script reports an existing symlink pointing elsewhere, stop and ask before replacing it.
