from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "reverse" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"


class ReverseSkillTests(unittest.TestCase):
    def test_reverse_skill_documents_full_workflow(self) -> None:
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: reverse", content)
        self.assertIn("/reverse", content)
        self.assertIn("reverse engineer", content)
        self.assertIn("protection level", content)
        self.assertIn("protocol fingerprint", content)
        self.assertIn("call chain", content)
        self.assertIn("PoC", content)
        self.assertIn("FACTS", content)
        self.assertIn("INFERENCES", content)
        self.assertIn("UNKNOWNS", content)
        self.assertIn("batch registration", content)
        self.assertIn("9-section", content)
        self.assertIn("T0", content)
        self.assertIn("T3", content)
        self.assertIn("fake signature", content)
        self.assertIn("Workflow", content)
        self.assertIn("Boundaries", content)
        self.assertIn("Educational and authorized use only", content)
        self.assertIn("Observe first, match later", content)
        self.assertIn("custom protocol fingerprint", content)

    def test_reference_files_exist(self) -> None:
        refs_dir = REPO_ROOT / "reverse" / "references"
        self.assertTrue((refs_dir / "protection-levels.md").exists(),
                        "protection-levels.md missing")
        self.assertTrue((refs_dir / "protocol-fingerprints.md").exists(),
                        "protocol-fingerprints.md missing")
        self.assertTrue((refs_dir / "search-strategy.md").exists(),
                        "search-strategy.md missing")
        self.assertTrue((refs_dir / "report-template.md").exists(),
                        "report-template.md missing")
        self.assertTrue((refs_dir / "fiu-framework.md").exists(),
                        "fiu-framework.md missing")

    def test_script_files_exist(self) -> None:
        scripts_dir = REPO_ROOT / "reverse" / "scripts"
        self.assertTrue((scripts_dir / "poc-fake-signature.js").exists(),
                        "poc-fake-signature.js missing")
        self.assertTrue((scripts_dir / "replay-template.js").exists(),
                        "replay-template.js missing")

    def test_readme_lists_reverse(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")

        self.assertIn("### 🔓 reverse", content)
        self.assertIn("[SKILL.md](./reverse/SKILL.md)", content)
        self.assertIn("/reverse <URL>", content)
        self.assertIn("Skills-13", content)


if __name__ == "__main__":
    unittest.main()
