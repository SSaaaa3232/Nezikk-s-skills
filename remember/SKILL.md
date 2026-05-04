---
name: remember
description: Use when the user enters /remember after running another skill and wants the lessons from that run, including detours, failures, fallback steps, verification gaps, or user corrections, written back into the corresponding SKILL.md in the Nezikk-s-skills repository so future Claude/Codex runs avoid the same problem.
---

# remember

Use this skill when the user types `/remember`, especially right after a skill was run and exposed a problem, detour, missing fallback, wrong assumption, or better verification method.

Examples:

```text
/remember
/remember obsidian
/remember image: 不要把截图失败当成保存失败
```

## Goal

Turn a lesson from the current conversation into durable skill instructions in the `Nezikk-s-skills` repository. The output should be an improved target `SKILL.md`, not a separate note.

## Workflow

1. Identify the target skill.
   - If `/remember` is followed by a skill name, use that name.
   - Otherwise infer the most recently executed non-`remember` skill from the conversation.
   - Search the repository for matching `SKILL.md` files:

```bash
find /Users/saaaaa/Desktop/Nezikk-s-skills -name SKILL.md -not -path '*/.git/*'
```

   - Prefer an exact frontmatter `name:` match, then an exact folder-name match.
   - If multiple matches remain, stop and ask which skill to update.

2. Extract the lesson.
   - Review the recent conversation and commands.
   - Capture only reusable facts that will help future runs:
     - failed assumptions
     - tool quirks
     - required paths or identifiers
     - fallback steps that actually worked
     - verification commands that proved the result
     - user corrections or preferences
   - Do not record temporary noise, one-off logs, secrets, tokens, cookies, or private content.

3. Patch the target `SKILL.md`.
   - Update the relevant workflow, safety rule, fallback, or verification section.
   - Merge into existing instructions instead of appending a diary entry.
   - Use absolute dates for time-sensitive facts.
   - Keep the skill concise; remove stale or contradicted guidance when needed.
   - If the target skill is under `external/`, preserve attribution and make the smallest local override needed.

4. Add or update tests when the repository already has skill tests.
   - For root-level skills, add a focused `tests/test_<skill>_skill.py` when missing.
   - For an existing test, add assertions for the new durable rule.
   - Do not add broad snapshot tests.

5. Verify.
   - Run the focused test for the edited skill when present.
   - Run the full repository test suite when practical:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

   - Confirm the target is linked into Claude/Codex if it is meant to be runnable:

```bash
readlink ~/.agents/skills/<skill-name>
readlink ~/.claude/skills/<skill-name>
```

6. Commit and push only the files changed for this learning.
   - Do not stage unrelated dirty files.
   - Use a message like:

```bash
git commit -m "docs: remember <skill-name> workflow lesson"
```

7. Report the result.
   - Target skill updated
   - Specific lesson captured
   - Tests run
   - Commit hash and push status
   - Any unrelated dirty files left untouched

## Boundaries

- Do not optimize every skill. Update only the target skill for the lesson at hand.
- Do not rewrite a skill from scratch unless the existing workflow is clearly broken.
- Do not edit system skills under `~/.codex/skills/.system`.
- Do not claim a lesson is remembered unless it has been written to disk and verified.
- If the issue is repository-wide health rather than one skill's run behavior, recommend creating or using a separate `skill-health` workflow.
