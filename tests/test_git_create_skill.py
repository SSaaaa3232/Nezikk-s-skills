from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "git-create" / "SKILL.md"


class GitCreateSkillTests(unittest.TestCase):
    def test_git_create_skill_requires_confirmations_and_gh_flow(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: git-create", content)
        self.assertIn("/git-create", content)
        self.assertIn("确认本地项目文件夹", content)
        self.assertIn("确认 GitHub 仓库名", content)
        self.assertIn("默认使用项目文件夹名", content)
        self.assertIn("默认创建 private", content)
        self.assertIn("gh auth status", content)
        self.assertIn("gh repo create", content)
        self.assertIn("--source", content)
        self.assertIn("--remote origin", content)
        self.assertIn("git init", content)
        self.assertIn("git push -u origin main", content)

    def test_git_create_skill_handles_existing_remote_safely(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("已有 remote", content)
        self.assertIn("不要覆盖", content)
        self.assertIn("让用户确认", content)


if __name__ == "__main__":
    unittest.main()
