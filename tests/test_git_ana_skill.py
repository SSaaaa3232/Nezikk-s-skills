from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "git-ana" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"


class GitAnaSkillTests(unittest.TestCase):
    def test_git_ana_skill_documents_github_analysis_workflow(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: git-ana", content)
        self.assertIn("/git-ana", content)
        self.assertIn("GitHub repository URL", content)
        self.assertIn("beginner-friendly technical analysis", content)
        self.assertIn("Gather evidence from the repository", content)
        self.assertIn("package.json", content)
        self.assertIn("pyproject.toml", content)
        self.assertIn("Dockerfile", content)
        self.assertIn("技术栈地图", content)
        self.assertIn("小白版运行逻辑", content)
        self.assertIn("Do not execute unknown project code", content)

    def test_readme_lists_git_ana(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")

        self.assertIn("### 🔎 git-ana", content)
        self.assertIn("[SKILL.md](./git-ana/SKILL.md)", content)
        self.assertIn("/git-ana <GitHub链接>", content)


if __name__ == "__main__":
    unittest.main()
