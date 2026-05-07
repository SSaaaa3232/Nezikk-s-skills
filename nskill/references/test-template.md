# Test File Template

Use this template when generating test files for nskill-created skills. Replace `<>` placeholders.

```python
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "<skill-name>" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"


class <ClassName>Tests(unittest.TestCase):
    def test_<name>_skill_documents_full_workflow(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        # Frontmatter fields
        self.assertIn("name: <skill-name>", content)
        self.assertIn("description:", content)
        self.assertIn("allowed-tools:", content)
        self.assertIn("model:", content)

        # Trigger command
        self.assertIn("/<skill-name>", content)

        # Key words from function description
        <for each key functionality>
        self.assertIn("<key-word>", content)
        </for>

        # Structural requirements
        self.assertIn("Workflow", content)
        self.assertIn("Boundaries", content)
        <if safety-critical>
        self.assertIn("<safety-rule-keyword>", content)
        </if>

    <if references exist>
    def test_reference_files_exist(self) -> None:
        refs_dir = REPO_ROOT / "<skill-name>" / "references"
        self.assertTrue((refs_dir / "<ref-file>.md").exists(),
                        "<ref-file>.md missing")
    </if>

    <if scripts exist>
    def test_script_files_exist(self) -> None:
        scripts_dir = REPO_ROOT / "<skill-name>" / "scripts"
        self.assertTrue((scripts_dir / "<script-file>.js").exists(),
                        "<script-file>.js missing")
    </if>

    def test_readme_lists_<name>(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")

        self.assertIn("### <emoji> <skill-name>", content)
        self.assertIn("[SKILL.md](./<skill-name>/SKILL.md)", content)
        self.assertIn("/<skill-name>", content)
        <if badge>
        self.assertIn("Skills-<N>", content)  # verify badge count updated
        </if>


if __name__ == "__main__":
    unittest.main()
```

## Test Coverage Checklist

Every generated test should verify:

### SKILL.md Structure
- [ ] frontmatter: `name`
- [ ] frontmatter: `description`
- [ ] frontmatter: `allowed-tools`
- [ ] frontmatter: `model`
- [ ] body: trigger command (`/<skill-name>`)
- [ ] body: key words from function description
- [ ] body: `Workflow` section
- [ ] body: `Boundaries` or safety section

### File Integrity (if applicable)
- [ ] references/ files exist
- [ ] scripts/ files exist
- [ ] scripts/ files pass syntax check

### README Registration
- [ ] Skill card heading present
- [ ] Link to SKILL.md correct
- [ ] Skill badge count incremented
