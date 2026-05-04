from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "remember" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"


class RememberSkillTests(unittest.TestCase):
    def test_remember_skill_documents_learning_workflow(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: remember", content)
        self.assertIn("/remember", content)
        self.assertIn("Nezikk-s-skills", content)
        self.assertIn("corresponding SKILL.md", content)
        self.assertIn("most recently executed", content)
        self.assertIn("failed assumptions", content)
        self.assertIn("fallback steps", content)
        self.assertIn("verification commands", content)
        self.assertIn("Do not stage unrelated dirty files", content)
        self.assertIn("python3 -m unittest discover", content)

    def test_readme_lists_remember(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")

        self.assertIn("### 🧠 remember", content)
        self.assertIn("[SKILL.md](./remember/SKILL.md)", content)
        self.assertIn("/remember", content)


if __name__ == "__main__":
    unittest.main()
