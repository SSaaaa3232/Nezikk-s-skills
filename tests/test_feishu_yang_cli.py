import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "feishu-yang-common" / "scripts" / "feishu_yang_cli.py"
SPEC = importlib.util.spec_from_file_location("feishu_yang_cli", CLI_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FeishuYangCliHelperTests(unittest.TestCase):
    def test_require_settings_reports_missing_values(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "FEISHU_APP_ID"):
            MODULE.require_settings({})

    def test_make_batch_dir_name_uses_timestamp_and_label(self) -> None:
        value = MODULE.make_batch_dir_name("20260425-143522", "yang-files")
        self.assertEqual(value, "20260425-143522-yang-files")

    def test_resolve_duplicate_filename_appends_counter(self) -> None:
        output_dir = Path("/tmp/yang-downloads-test")
        first = MODULE.resolve_output_path(output_dir, "report.pdf", set())
        second = MODULE.resolve_output_path(output_dir, "report.pdf", {first.name})
        self.assertEqual(first.name, "report.pdf")
        self.assertEqual(second.name, "report-2.pdf")

    def test_resolve_output_path_rejects_invalid_special_filenames(self) -> None:
        output_dir = Path("/tmp/yang-downloads-test")
        for invalid in ("", ".", ".."):
            with self.assertRaises(ValueError):
                MODULE.resolve_output_path(output_dir, invalid, set())

    def test_resolve_output_path_avoids_existing_file_on_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            (output_dir / "report.pdf").write_text("existing", encoding="utf-8")
            resolved = MODULE.resolve_output_path(output_dir, "report.pdf", set())
            self.assertEqual(resolved.name, "report-2.pdf")


if __name__ == "__main__":
    unittest.main()
