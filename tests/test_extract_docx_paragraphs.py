import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "synbio-academic-translator" / "scripts" / "extract_docx_paragraphs.py"


class ExtractDocxParagraphsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self.tmp.name)
        self.sample = self.tmp_dir / "sample.docx"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_minimal_docx(self, path: Path, paragraphs: list[list[str]]) -> None:
        body_parts: list[str] = []
        for runs in paragraphs:
            run_xml = "".join(f"<w:r><w:t>{escape(run)}</w:t></w:r>" for run in runs)
            body_parts.append(f"<w:p>{run_xml}</w:p>")
        body = "".join(body_parts)
        document_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body>{body}</w:body>"
            "</w:document>"
        )
        with ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", document_xml)

    def test_extracts_chinese_paragraphs_from_docx(self) -> None:
        self._write_minimal_docx(
            self.sample,
            [
                ["Differential Impacts of ", "Calcineurin signaling Pathway Genes"],
                ["引", "言"],
                ["L-苹果酸作为一种重要的四碳", "二羧酸"],
            ],
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.sample)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "引言",
                "L-苹果酸作为一种重要的四碳二羧酸",
            ],
        )

    def test_requires_existing_docx_file(self) -> None:
        missing = self.tmp_dir / "missing.docx"
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
