import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "synbio-academic-translator" / "scripts" / "extract_docx_paragraphs.py"
SAMPLE = Path("/Users/saaaaa/Desktop/论文中译英/CSP通路在黑曲霉生产20260303引言.docx")


class ExtractDocxParagraphsTests(unittest.TestCase):
    def test_extracts_chinese_paragraphs_from_docx(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(SAMPLE)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("引言", result.stdout)
        self.assertIn("L-苹果酸作为一种重要的四碳二羧酸", result.stdout)
        self.assertNotIn(
            "Differential Impacts of Calcineurin signaling Pathway Genes",
            result.stdout,
        )

    def test_requires_existing_docx_file(self) -> None:
        missing = SAMPLE.with_name("missing.docx")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(missing)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not exist", result.stderr)


if __name__ == "__main__":
    unittest.main()
