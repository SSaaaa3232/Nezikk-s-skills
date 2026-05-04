from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "repeat" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"


class RepeatSkillTests(unittest.TestCase):
    def test_repeat_skill_documents_requirement_alignment_workflow(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: repeat", content)
        self.assertIn("/repeat", content)
        self.assertIn("restate the requirement", content)
        self.assertIn("align the user's intent", content)
        self.assertIn("goals, constraints, assumptions, and next steps", content)
        self.assertIn("Preserve important names, paths, commands, URLs", content)
        self.assertIn("confirmed facts from assumptions", content)
        self.assertIn("Do not execute the repeated request", content)
        self.assertIn("你的意思是", content)
        self.assertIn("关键约束", content)

    def test_readme_lists_repeat(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")

        self.assertIn("### 🔁 repeat", content)
        self.assertIn("[SKILL.md](./repeat/SKILL.md)", content)
        self.assertIn("/repeat <内容>", content)


if __name__ == "__main__":
    unittest.main()
