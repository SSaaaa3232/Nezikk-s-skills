from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "git-ana" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"


class GitAnaSkillTests(unittest.TestCase):
    def test_git_ana_has_industrial_frontmatter(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: git-ana", content)
        self.assertIn("description:", content)
        self.assertIn("allowed-tools:", content, "missing tool boundaries")
        self.assertIn("model:", content, "missing model assignment")

    def test_git_ana_documents_methodology_workflow(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("/git-ana", content)
        self.assertIn("GitHub URL", content)
        self.assertIn("技术选型决策树", content)
        self.assertIn("架构构建推演", content)
        self.assertIn("关键实现分析", content)
        self.assertIn("证据表", content)
        self.assertIn("FACTS / INFERENCES / UNKNOWNS", content)
        self.assertIn("复现路径", content)
        self.assertIn("作者", content)  # methodology focuses on author's decisions
        self.assertIn("Confidence", content)
        self.assertIn("HIGH/MEDIUM/LOW", content)

    def test_git_ana_has_chinese_triggers(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("分析一下这个项目怎么构建的", content)
        self.assertIn("作者是怎么从零搭建的", content)
        self.assertIn("技术选型有什么依据", content)

    def test_git_ana_has_safety_and_boundaries(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Do not execute unknown project code", content)
        self.assertIn("Do not run install scripts", content)
        self.assertIn("Do not clone private repositories", content)
        self.assertIn("methodology", content.lower())

    def test_git_ana_has_verification(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("evidence table", content)
        self.assertIn("chain of reasoning", content)
        self.assertIn("FACTS", content)

    def test_git_ana_requires_methodology_summary_box(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("方法论总结", content)
        self.assertIn("ASCII", content)
        self.assertIn("Phase", content)  # flow box uses Phase naming

    def test_git_ana_caps_author_intent_inference_at_medium(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Author intent inferences cap at MEDIUM", content)
        self.assertIn("unless the author explicitly stated", content)
        self.assertIn("commit message", content)
        self.assertIn("direct quote", content)

    def test_readme_lists_git_ana(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")

        self.assertIn("### 🔎 git-ana", content)
        self.assertIn("[SKILL.md](./git-ana/SKILL.md)", content)
        self.assertIn("/git-ana", content)


if __name__ == "__main__":
    unittest.main()
