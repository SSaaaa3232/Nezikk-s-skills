from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "nskill" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"


class NSkillSkillTests(unittest.TestCase):
    def test_nskill_frontmatter_has_industrial_fields(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: nskill", content)
        self.assertIn("description:", content)
        self.assertIn("allowed-tools:", content, "missing tool boundaries")
        self.assertIn("model:", content, "missing model assignment")

    def test_nskill_trigger_and_command(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("/nskill", content)
        self.assertIn("function description", content)
        self.assertIn("skill name", content)
        self.assertIn("/<skill-name>", content)
        self.assertIn("创建一个新skill", content)  # covers Chinese trigger phrases

    def test_nskill_documents_full_publish_flow(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Nezikk-s-skills", content)
        self.assertIn("SKILL.md", content)
        self.assertIn("./scripts/link-skill.sh <skill-name>", content)
        self.assertIn("readlink ~/.agents/skills/<skill-name>", content)
        self.assertIn("README.md", content)
        self.assertIn("git commit", content)
        self.assertIn("git push", content)
        self.assertIn("unittest discover", content)

    def test_nskill_documents_verification_framework(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("File Integrity Check", content)
        self.assertIn("Trigger Eval", content)
        self.assertIn("Execution Eval", content)
        self.assertIn("Baseline Comparison", content)

    def test_nskill_documents_eval_and_iteration(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("After Creation", content)
        self.assertIn("Scoring Rubric", content)
        self.assertIn("minimum acceptable score", content.lower())
        self.assertIn("Optimization Loop", content)

    def test_nskill_has_safety_and_boundaries(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Do not create folders outside", content)
        self.assertIn("Do not overwrite existing files", content)
        self.assertIn("frontmatter", content)
        self.assertIn("Workflow", content)
        self.assertIn("Boundaries", content)

    def test_nskill_reference_files_exist(self) -> None:
        refs_dir = REPO_ROOT / "nskill" / "references"

        self.assertTrue((refs_dir / "skill-skeleton.md").exists(),
                        "skill-skeleton.md missing")
        self.assertTrue((refs_dir / "test-template.md").exists(),
                        "test-template.md missing")

    def test_nskill_skeleton_has_industrial_standards(self) -> None:
        content = (REPO_ROOT / "nskill" / "references" / "skill-skeleton.md").read_text(encoding="utf-8")

        self.assertIn("allowed-tools:", content)
        self.assertIn("model:", content)
        self.assertIn("description:", content)
        self.assertIn("Workflow", content)
        self.assertIn("Boundaries", content)
        self.assertIn("frontmatter", content.lower())
        self.assertIn("least privilege", content.lower())

    def test_readme_lists_nskill(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")

        self.assertIn("### 🧩 nskill", content)
        self.assertIn("[SKILL.md](./nskill/SKILL.md)", content)


if __name__ == "__main__":
    unittest.main()
