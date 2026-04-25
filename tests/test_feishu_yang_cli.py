import importlib.util
import tempfile
import unittest
from urllib import request as urllib_request
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

    def test_filter_recent_file_messages_excludes_equal_boundary_timestamp(self) -> None:
        messages = [
            {
                "message_id": "m-equal",
                "message_type": "file",
                "create_time": "1714000000000",
                "sender": {
                    "sender_name": "Yang",
                    "sender_id": {"open_id": "ou_yang"},
                },
                "body": {"file_key": "fk-eq", "file_name": "equal.pdf"},
            },
            {
                "message_id": "m-newer",
                "message_type": "file",
                "create_time": "1714000000001",
                "sender": {
                    "sender_name": "Yang",
                    "sender_id": {"open_id": "ou_yang"},
                },
                "body": {"file_key": "fk-new", "file_name": "newer.pdf"},
            },
        ]
        filtered = MODULE.filter_recent_file_messages(
            messages,
            sender_name="Yang",
            sender_open_id="ou_yang",
            min_created_ms=1714000000000,
        )
        self.assertEqual([item["message_id"] for item in filtered], ["m-newer"])

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


class FeishuYangCliHttpTests(unittest.TestCase):
    def test_request_json_sends_request_and_parses_response(self) -> None:
        response = mock.MagicMock()
        response.read.return_value = b'{"code":0,"data":{"ok":true}}'
        context = mock.MagicMock()
        context.__enter__.return_value = response

        with mock.patch.object(MODULE.urllib.request, "urlopen", return_value=context) as mocked_open:
            result = MODULE.request_json(
                "https://example.test/open-apis/ping",
                method="POST",
                payload=b'{"hello":"world"}',
                headers={"Content-Type": "application/json"},
            )

        self.assertEqual(result["code"], 0)
        self.assertEqual(result["data"], {"ok": True})
        sent_request = mocked_open.call_args[0][0]
        self.assertIsInstance(sent_request, urllib_request.Request)
        self.assertEqual(sent_request.get_method(), "POST")
        self.assertEqual(sent_request.full_url, "https://example.test/open-apis/ping")
        self.assertEqual(sent_request.data, b'{"hello":"world"}')

    def test_send_json_serializes_payload_and_calls_request_json(self) -> None:
        with mock.patch.object(MODULE, "request_json", return_value={"code": 0}) as mocked_request_json:
            MODULE.send_json(
                "https://example.test/open-apis/mock",
                {"k": "v"},
                {"Authorization": "Bearer token"},
            )
        kwargs = mocked_request_json.call_args.kwargs
        self.assertEqual(kwargs["url"], "https://example.test/open-apis/mock")
        self.assertEqual(kwargs["method"], "POST")
        self.assertEqual(kwargs["payload"], b'{"k":"v"}')
        self.assertEqual(kwargs["headers"]["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer token")

    def test_fetch_tenant_access_token_posts_to_internal_endpoint(self) -> None:
        with mock.patch.object(
            MODULE,
            "send_json",
            return_value={"code": 0, "tenant_access_token": "t-123"},
        ) as mocked_send_json:
            token = MODULE.fetch_tenant_access_token("cli_id", "cli_secret")
        self.assertEqual(token, "t-123")
        args = mocked_send_json.call_args.args
        self.assertEqual(
            args[0],
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        )
        self.assertEqual(args[1], {"app_id": "cli_id", "app_secret": "cli_secret"})
        self.assertEqual(args[2], {})

    def test_build_multipart_form_builds_form_data_for_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "report.txt"
            file_path.write_bytes(b"hello")
            content_type, body = MODULE.build_multipart_form("file", file_path)
        self.assertIn("multipart/form-data; boundary=", content_type)
        self.assertIn(b'Content-Disposition: form-data; name="file"; filename="report.txt"', body)
        self.assertIn(b"hello", body)

    def test_feishu_client_list_recent_files_filters_after_http_fetch(self) -> None:
        with mock.patch.object(MODULE, "fetch_tenant_access_token", return_value="tenant-token"):
            client = MODULE.FeishuClient("app_id", "app_secret")
        with mock.patch.object(
            MODULE,
            "request_json",
            return_value={
                "code": 0,
                "data": {
                    "items": [
                        {
                            "message_id": "m-1",
                            "message_type": "file",
                            "create_time": "1714000000100",
                            "sender": {
                                "sender_name": "Yang",
                                "sender_id": {"open_id": "ou_yang"},
                            },
                            "body": {"file_key": "fk-1", "file_name": "ok.pdf"},
                        },
                        {
                            "message_id": "m-2",
                            "message_type": "text",
                            "create_time": "1714000000200",
                            "sender": {
                                "sender_name": "Yang",
                                "sender_id": {"open_id": "ou_yang"},
                            },
                            "body": {},
                        },
                    ]
                },
            },
        ) as mocked_request_json, mock.patch.object(MODULE.time, "time", return_value=1714000000.2):
            items = client.list_recent_files(
                chat_id="oc_test_chat",
                sender_name="Yang",
                sender_open_id="ou_yang",
                hours=1,
            )
        self.assertEqual([item["message_id"] for item in items], ["m-1"])
        request_kwargs = mocked_request_json.call_args.kwargs
        self.assertEqual(request_kwargs["method"], "GET")
        self.assertIn("chats/oc_test_chat/messages", request_kwargs["url"])
        self.assertIn("page_size=50", request_kwargs["url"])
        self.assertEqual(
            request_kwargs["headers"]["Authorization"],
            "Bearer tenant-token",
        )

    def test_feishu_client_download_file_writes_binary_to_path(self) -> None:
        with mock.patch.object(MODULE, "fetch_tenant_access_token", return_value="tenant-token"):
            client = MODULE.FeishuClient("app_id", "app_secret")
        response = mock.MagicMock()
        response.read.return_value = b"PDFDATA"
        context = mock.MagicMock()
        context.__enter__.return_value = response
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            MODULE.urllib.request, "urlopen", return_value=context
        ):
            output_path = Path(tmp) / "out.pdf"
            client.download_file("file_key_1", output_path)
            self.assertEqual(output_path.read_bytes(), b"PDFDATA")

    def test_feishu_client_upload_file_posts_multipart_and_returns_file_key(self) -> None:
        with mock.patch.object(MODULE, "fetch_tenant_access_token", return_value="tenant-token"):
            client = MODULE.FeishuClient("app_id", "app_secret")
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "doc.txt"
            source.write_text("payload", encoding="utf-8")
            with mock.patch.object(
                MODULE,
                "build_multipart_form",
                return_value=("multipart/form-data; boundary=test", b"--test--"),
            ) as mocked_multipart, mock.patch.object(
                MODULE,
                "request_json",
                return_value={"code": 0, "data": {"file_key": "fk-uploaded"}},
            ) as mocked_request_json:
                file_key = client.upload_file(source)
        self.assertEqual(file_key, "fk-uploaded")
        mocked_multipart.assert_called_once_with("file", source)
        kwargs = mocked_request_json.call_args.kwargs
        self.assertEqual(kwargs["method"], "POST")
        self.assertIn("/im/v1/files", kwargs["url"])
        self.assertEqual(kwargs["payload"], b"--test--")
        self.assertEqual(kwargs["headers"]["Content-Type"], "multipart/form-data; boundary=test")

    def test_feishu_client_send_file_message_posts_json_payload(self) -> None:
        with mock.patch.object(MODULE, "fetch_tenant_access_token", return_value="tenant-token"):
            client = MODULE.FeishuClient("app_id", "app_secret")
        with mock.patch.object(
            MODULE,
            "send_json",
            return_value={"code": 0, "data": {"message_id": "om_1"}},
        ) as mocked_send_json:
            response = client.send_file_message("oc_chat_1", "file_key_1")
        self.assertEqual(response["code"], 0)
        args = mocked_send_json.call_args.args
        self.assertEqual(
            args[0],
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        )
        self.assertEqual(
            args[1],
            {
                "receive_id": "oc_chat_1",
                "msg_type": "file",
                "content": '{"file_key":"file_key_1"}',
            },
        )
        self.assertEqual(args[2]["Authorization"], "Bearer tenant-token")


if __name__ == "__main__":
    unittest.main()
