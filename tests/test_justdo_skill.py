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

    def test_justdo_skill_documents_desktop_project_folder_creation(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("/justdo", content)
        self.assertIn("文件夹名字", content)
        self.assertIn("/Users/saaaaa/Desktop/项目", content)
        self.assertIn("mkdir -p", content)
        self.assertIn("目标文件夹已存在", content)
        self.assertIn("不要覆盖", content)


if __name__ == "__main__":
    unittest.main()
