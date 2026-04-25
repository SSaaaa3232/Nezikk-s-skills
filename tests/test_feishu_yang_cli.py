import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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

    def test_filter_recent_file_messages_matches_sender_and_time(self) -> None:
        messages = [
            {
                "message_id": "m-keep",
                "message_type": "file",
                "create_time": "1714000000001",
                "sender": {
                    "sender_name": "Yang",
                    "sender_id": {"open_id": "ou_yang"},
                },
                "body": {"file_key": "fk-1", "file_name": "ok.pdf"},
            },
            {
                "message_id": "m-old",
                "message_type": "file",
                "create_time": "1713999999999",
                "sender": {
                    "sender_name": "Yang",
                    "sender_id": {"open_id": "ou_yang"},
                },
                "body": {"file_key": "fk-2", "file_name": "old.pdf"},
            },
            {
                "message_id": "m-other-type",
                "message_type": "text",
                "create_time": "1714000001000",
                "sender": {
                    "sender_name": "Yang",
                    "sender_id": {"open_id": "ou_yang"},
                },
                "body": {},
            },
            {
                "message_id": "m-other-sender",
                "message_type": "file",
                "create_time": "1714000002000",
                "sender": {
                    "sender_name": "SomeoneElse",
                    "sender_id": {"open_id": "ou_else"},
                },
                "body": {"file_key": "fk-3", "file_name": "other.pdf"},
            },
        ]
        filtered = MODULE.filter_recent_file_messages(
            messages,
            sender_name="Yang",
            sender_open_id="ou_yang",
            min_created_ms=1714000000000,
        )
        self.assertEqual([item["message_id"] for item in filtered], ["m-keep"])

    def test_filter_recent_file_messages_tolerates_malformed_nested_values(self) -> None:
        messages = [
            {
                "message_id": "m-bad-sender",
                "message_type": "file",
                "create_time": "1714000000001",
                "sender": "not-a-dict",
                "body": {"file_key": "fk-x", "file_name": "bad-sender.pdf"},
            },
            {
                "message_id": "m-bad-sender-id",
                "message_type": "file",
                "create_time": "1714000000002",
                "sender": {
                    "sender_name": "Yang",
                    "sender_id": "not-a-dict",
                },
                "body": {"file_key": "fk-y", "file_name": "bad-sender-id.pdf"},
            },
            {
                "message_id": "m-keep",
                "message_type": "file",
                "create_time": "1714000000003",
                "sender": {
                    "sender_name": "Yang",
                    "sender_id": {"open_id": "ou_yang"},
                },
                "body": {"file_key": "fk-z", "file_name": "good.pdf"},
            },
        ]
        filtered = MODULE.filter_recent_file_messages(
            messages,
            sender_name="Yang",
            sender_open_id="ou_yang",
            min_created_ms=1714000000000,
        )
        self.assertEqual([item["message_id"] for item in filtered], ["m-keep"])

    def test_parse_selection_supports_csv_and_ranges(self) -> None:
        self.assertEqual(MODULE.parse_selection("1,3-4", max_index=5), [1, 3, 4])

    def test_parse_selection_rejects_invalid_or_out_of_range_values(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.parse_selection("0", max_index=5)
        with self.assertRaises(ValueError):
            MODULE.parse_selection("6", max_index=5)
        with self.assertRaises(ValueError):
            MODULE.parse_selection("4-2", max_index=5)
        with self.assertRaises(ValueError):
            MODULE.parse_selection("x", max_index=5)

    def test_prepare_batch_directory_creates_unique_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            first = MODULE.prepare_batch_directory(
                output_root, timestamp="20260425-150000", label="yang-files"
            )
            second = MODULE.prepare_batch_directory(
                output_root, timestamp="20260425-150000", label="yang-files"
            )
            self.assertTrue(first.is_dir())
            self.assertTrue(second.is_dir())
            self.assertEqual(first.name, "20260425-150000-yang-files")
            self.assertEqual(second.name, "20260425-150000-yang-files-2")

    def test_prepare_batch_directory_retries_on_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            (output_root / "20260425-150000-yang-files").mkdir()
            (output_root / "20260425-150000-yang-files-2").mkdir()

            created = MODULE.prepare_batch_directory(
                output_root, timestamp="20260425-150000", label="yang-files"
            )
            self.assertEqual(created.name, "20260425-150000-yang-files-3")
            self.assertTrue(created.is_dir())

    def test_prepare_batch_directory_handles_racy_file_exists_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            call_counter = {"value": 0}
            original_mkdir = Path.mkdir

            def flaky_mkdir(path_obj, *args, **kwargs):
                if path_obj == output_root / "20260425-150000-yang-files":
                    call_counter["value"] += 1
                    if call_counter["value"] == 1:
                        raise FileExistsError("simulated race")
                return original_mkdir(path_obj, *args, **kwargs)

            with mock.patch.object(Path, "mkdir", autospec=True, side_effect=flaky_mkdir):
                created = MODULE.prepare_batch_directory(
                    output_root, timestamp="20260425-150000", label="yang-files"
                )
            self.assertEqual(created.name, "20260425-150000-yang-files-2")
            self.assertTrue(created.is_dir())

    def test_serialize_candidate_extracts_file_fields(self) -> None:
        message = {
            "message_id": "m-1",
            "message_type": "file",
            "create_time": "1714000000001",
            "sender": {
                "sender_name": "Yang",
                "sender_id": {"open_id": "ou_yang"},
            },
            "body": {"file_key": "fk-1", "file_name": "ok.pdf"},
        }
        self.assertEqual(
            MODULE.serialize_candidate(message),
            {
                "message_id": "m-1",
                "file_key": "fk-1",
                "file_name": "ok.pdf",
                "sender_name": "Yang",
                "create_time": "1714000000001",
            },
        )

    def test_serialize_candidate_tolerates_malformed_nested_values(self) -> None:
        message = {
            "message_id": "m-malformed",
            "create_time": "1714000000002",
            "sender": "not-a-dict",
            "body": ["not-a-dict"],
        }
        self.assertEqual(
            MODULE.serialize_candidate(message),
            {
                "message_id": "m-malformed",
                "file_key": None,
                "file_name": None,
                "sender_name": None,
                "create_time": "1714000000002",
            },
        )


if __name__ == "__main__":
    unittest.main()
