from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
OLD_SKILL_PATH = REPO_ROOT / "just do" / "SKILL.md"
SKILL_PATH = REPO_ROOT / "justdo" / "SKILL.md"


class JustdoSkillTests(unittest.TestCase):
    def test_justdo_skill_uses_no_spaces_in_folder_or_name(self) -> None:
        self.assertFalse(OLD_SKILL_PATH.exists())
        self.assertTrue(SKILL_PATH.exists())

        content = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("name: justdo", content)
        self.assertIn("# justdo", content)
        self.assertNotIn("name: just do", content)


if __name__ == "__main__":
    unittest.main()
