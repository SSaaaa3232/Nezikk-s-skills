---
name: nskill
description: Use when the user enters /nskill with a skill name and optional function description. Also trigger when user says 创建一个新skill、帮我写一个skill、新建一个技能、给仓库加一个skill、用工业级标准新建skill、创建agent技能、写一个指令让agent. /nskill creates, tests, links, commits, and publishes a complete command skill to the Nezikk-s-skills repository following industrial-grade standards. The skill name is also the folder name, frontmatter name, and slash command trigger.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
model: opus
---

# NSkill

Use this skill when the user types `/nskill <name> <function description>` or asks in natural language to create a new skill. Also triggers on phrases like:

```text
/nskill repeat 复述用户要求
创建一个叫 xxx 的新 skill
帮我写一个 xxx 的 skill，功能是...
给仓库加一个 skill
用工业级标准新建一个 skill
```

This creates:

```text
<name>/                  # folder
<name>/SKILL.md          # skill file with frontmatter
name: <name>             # frontmatter name
/<name>                  # slash command trigger documented in the skill
```

## Goal

Turn one skill request into an **industrial-grade** skill that is: correctly triggered, tool-bounded, progressively disclosed, tested, linked, committed, pushed, **and verified** — including trigger eval, execution eval, and baseline comparison.

## Workflow

### 1. Parse
- Parse the text after `/nskill`.
- Trim spaces and matching quotes (ASCII + Chinese quotes).
- First token = `skill name`. Everything after = `function description`.
- Skill name = folder name, frontmatter `name`, slash command trigger `/<skill-name>`.
- Ask for a valid name if empty, contains `/`, starts with `.`, or is `.` / `..`.
- Prefer lowercase kebab-case.
- If function description is missing, ask unless the user explicitly requested scaffold-only.

### 2. Locate Repository
- Work from the `Nezikk-s-skills` repository root.
- If inside a worktree, use that worktree root.
- If elsewhere, locate or ask for the path.

### 3. Create Folder
- Create `<skill-name>/` folder at repo root.
- Stop if it already exists, unless the user explicitly asks to update.
- Also create `references/` and `scripts/` subdirectories if the function description needs them.

### 4. Write SKILL.md
- Use the skeleton in `references/skill-skeleton.md` as template.
- Frontmatter MUST include: `name`, `description`, `allowed-tools`, `model`.
- `allowed-tools`: give only the tools needed for the task. Default: `Bash, Read, Write, Grep`. Add `Edit` only if modifying files. Add `WebFetch` only if fetching URLs. Never give `Agent` unless explicitly requested.
- `model`: select based on the task's **reasoning demand**, not a fixed name. Write the value that your platform understands (Claude: `opus`/`sonnet`/`haiku`, Codex: `gpt-5`/`o4-mini`, others: equivalent). The mapping is:

  | Need | Capability | Claude | Codex (example) |
  |------|-----------|--------|-----------------|
  | Heavy reasoning, multi-step analysis, code generation | **Strong** | `opus` | `gpt-5` |
  | Structured output, reports, docs, balanced speed/quality | **Balanced** | `sonnet` | `o4-mini` or `gpt-5` |
  | Simple lookup, keyword check, classification | **Fast** | `haiku` | `o4-mini` |

  Choose one tier above. The agent reading this SKILL.md maps it to whatever is available on its runtime. **Prefer the platform-native model name in the frontmatter value** so the runtime can parse it directly.
- Body MUST document: trigger format, examples in user's natural language, goal, workflow steps, output style, verification steps, boundaries/safety rules.
- Keep under 500 lines. Put long docs in `references/`, stable ops in `scripts/`, templates/samples in `assets/`.
- The skill MUST be immediately usable when the user types `/<skill-name> ...`.

### 5. Add References/Scripts/Assets (if needed)
- `references/` — long docs, protocol specs, style guides, detailed examples, search strategies. **Reference files are NOT loaded on trigger, only when the agent explicitly reads them during workflow execution.**
- `scripts/` — deterministic operations that shouldn't rely on LLM generation each time (file checks, format validation, template generation).
- `assets/` — templates, schemas, sample output files, font/color configs.
- Only create what the description truly needs. Do not create empty placeholder directories.

### 6. Create Test
- Create `tests/test_<snake_case_name>_skill.py` using the template in `references/test-template.md`.
- Test that `SKILL.md` contains: frontmatter fields (`name`, `description`, `allowed-tools`, `model`), trigger command, key words from function description, `Workflow`, `Boundaries` or safety rules.
- Test that `README.md` lists the new skill with correct link.
- If the skill has reference/script files, add existence checks.

### 7. Update README.md
- Increase the Skills badge count by 1.
- Add skill to the "My Skills" table.
- Add a skill card section under "Skills" explaining: what it does, when to use it, what it will do, link to `SKILL.md`.

### 8. Link and Verify

Run link script:
```bash
./scripts/link-skill.sh <skill-name>
```

Confirm symlinks:
```bash
readlink ~/.agents/skills/<skill-name>
readlink ~/.claude/skills/<skill-name>
```

**Full verification — do ALL of the following before committing:**

#### 8a. File Integrity Check
```bash
test -f <skill-name>/SKILL.md && echo "✅ SKILL.md exists"
grep -q "name: <skill-name>" <skill-name>/SKILL.md && echo "✅ frontmatter name correct"
grep -q "description:" <skill-name>/SKILL.md && echo "✅ description present"
grep -q "allowed-tools:" <skill-name>/SKILL.md && echo "✅ tool boundaries set"
grep -q "model:" <skill-name>/SKILL.md && echo "✅ model assigned"
grep -q "/<skill-name>" <skill-name>/SKILL.md && echo "✅ trigger command documented"
grep -q "Workflow" <skill-name>/SKILL.md && echo "✅ Workflow section"
grep -q "Boundaries" <skill-name>/SKILL.md && echo "✅ Boundaries section"
```

#### 8b. Trigger Eval — Test at least 8 natural-language phrases
Prepare a mix of phrases that SHOULD trigger and SHOULD NOT trigger the new skill. Check that the description contains enough keywords to match the positive cases and exclude the negative cases.

Consider user phrasings like:
- 命令形式: `/<skill-name> ...`
- 自然语言: task-related natural language queries
- 变体: different ways to express the same task

If trigger coverage < 80%, expand the description.

#### 8c. Execution Eval — Run a real task
Use the newly created skill on a known test case (a task you already know the expected output for). Verify:
- The workflow steps execute in order
- Reference files are readable when needed
- Scripts execute without syntax errors
- Output format matches the expected style

#### 8d. Baseline Comparison (if applicable)
If the task was previously possible without the skill, note the difference:
- Without skill: what did the agent miss or do inefficiently?
- With skill: does it add missing steps, enforce structure, prevent errors?

#### 8e. Run all repository tests
```bash
cd <repo-root> && python3 -m unittest discover -s tests -p 'test_*.py' -v
```

### 9. Publish

Stage only files related to the new skill:
```bash
git add <skill-name>/SKILL.md tests/test_<snake_case_name>_skill.py README.md
# also add references/, scripts/, assets/ if created
```

Commit and push:
```bash
git commit -m "feat: add <skill-name> skill"
git push
```

### 10. Report
Report the created folder path, trigger command, verification result (all 5 sub-steps of step 8), symlink result, commit hash, and push result.

---

## After Creation: Verify, Score, Iterate

A skill is not complete after creation. Guide the user through the verification loop:

### The Optimization Loop

```
Write Skill → Prepare test data → Run eval → Score each case
    → Find failures → Fix Skill → Re-run eval
    → Reach minimum acceptable score, or at least know its boundaries
```

### Scoring Rubric (0-10 per case)

- **0-2**: Did not complete the task or went in the wrong direction
- **3-4**: Barely related, missed key requirements
- **5-6**: Basically usable but has obvious issues
- **7-8**: Stable quality, minor details to improve
- **9-10**: Excellent, can serve as demonstration output

**Minimum standard**: Core test cases must score ≥ 5.

### What to Fix Based on Scores

| Symptom | Fix |
|---------|-----|
| Not triggered | Add trigger phrases to description |
| False trigger | Narrow description, add "when NOT to trigger" |
| Steps missed | Update workflow steps in SKILL.md |
| Output format inconsistent | Add output examples to assets/ |
| Deterministic check fails | Move to scripts/ |
| Reference too long | Split to references/ |
| Tool permission missing | Expand allowed-tools |
| Tool permission excessive | Tighten allowed-tools |
| Model too weak for task | Upgrade model in frontmatter |

---

## Self-Eval: How to Verify NSkill Itself

This skill generates other skills, so verifying it means **verifying the generated skill**.

### Test Data

For each skill creation, test the generated skill against these prompts:

| Case | Trigger Phrase | Expected Result |
|------|---------------|-----------------|
| slash command | `/<skill-name> <arg>` | Triggers |
| natural language 1 | Task-related phrase | Triggers |
| natural language 2 | Alternative expression | Triggers |
| false positive 1 | Related but different domain | Does NOT trigger |
| false positive 2 | Generic question | Does NOT trigger |

### Execution Test

On a known test case (a simple task where the user already knows the correct answer), run the generated skill and verify:
1. All workflow steps execute in order
2. Output format matches the documented output style
3. Safety boundaries are respected

### Scoring the Generated Skill

| Dimension | Weight | Check |
|-----------|--------|-------|
| Trigger accuracy | 30% | Triggers on target, silent otherwise |
| Workflow completeness | 25% | All necessary steps present |
| Output quality | 25% | Format matches spec, evidence anchors present |
| Safety boundaries | 20% | Danger cases handled, unauthorized ops blocked |

### When NSkill Itself Should Improve

If a skill generated by NSkill repeatedly fails on the same dimension, fix NSkill's template/skeleton/references — not just the individual generated skill.

---

## Notes

- Do not create folders outside `Nezikk-s-skills`.
- Do not overwrite existing files unless the user requests an update.
- If unrelated tests fail, report and ask before pushing.
- Do not create a minimal placeholder when the user provided a function description.
- The skill name IS the command. `/nskill repeat ...` → `/repeat ...`.
- **Every generated skill MUST include at minimum**: allowed-tools, model, trigger examples, Workflow, Boundaries.
- **Every generated skill SHOULD include**: references/ for long content, scripts/ for deterministic ops.
