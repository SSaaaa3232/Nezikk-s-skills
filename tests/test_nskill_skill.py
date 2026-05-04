from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "nskill" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"


class NSkillSkillTests(unittest.TestCase):
    def test_nskill_skill_documents_command_and_publish_flow(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: nskill", content)
        self.assertIn("/nskill", content)
        self.assertIn("/nskill <name> <function description>", content)
        self.assertIn("Nezikk-s-skills", content)
        self.assertIn("function description", content)
        self.assertIn("slash command trigger", content)
        self.assertIn("/<skill-name>", content)
        self.assertIn("skill-creator", content)
        self.assertIn("SKILL.md", content)
        self.assertIn("tests/test_<skill_name_with_underscores>_skill.py", content)
        self.assertIn("./scripts/link-skill.sh <skill-name>", content)
        self.assertIn("readlink ~/.agents/skills/<skill-name>", content)
        self.assertIn("README.md", content)
        self.assertIn("git status", content)
        self.assertIn("git commit", content)
        self.assertIn("git push", content)
        self.assertIn("Do not create only a minimal placeholder", content)
        self.assertIn("callable as `/<skill-name> ...`", content)

    def test_readme_lists_nskill(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")

        self.assertIn("### 🧩 nskill", content)
        self.assertIn("[SKILL.md](./nskill/SKILL.md)", content)


if __name__ == "__main__":
    unittest.main()
