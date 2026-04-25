import argparse
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from urllib import request as urllib_request
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "feishu-yang-automation" / "scripts" / "feishu_yang_cli.py"
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
        value = MODULE.make_batch_dir_name("2026.4.25", "1")
        self.assertEqual(value, "2026.4.25-1")

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

    def test_filter_recent_file_messages_supports_real_feishu_shapes(self) -> None:
        messages = [
            {
                "message_id": "m-file",
                "msg_type": "file",
                "create_time": "1714000000001",
                "sender": {"id": "ou_yang", "id_type": "open_id"},
                "body": {"content": '{"file_key":"fk_1","file_name":"paper.pdf"}'},
            },
            {
                "message_id": "m-text",
                "msg_type": "text",
                "create_time": "1714000000002",
                "sender": {"id": "ou_yang", "id_type": "open_id"},
                "body": {"content": '{"text":"hi"}'},
            },
        ]
        filtered = MODULE.filter_recent_file_messages(
            messages,
            sender_name="",
            sender_open_id="ou_yang",
            min_created_ms=1714000000000,
        )
        self.assertEqual([item["message_id"] for item in filtered], ["m-file"])

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
                output_root, timestamp="2026.4.25", label=""
            )
            second = MODULE.prepare_batch_directory(
                output_root, timestamp="2026.4.25", label=""
            )
            self.assertTrue(first.is_dir())
            self.assertTrue(second.is_dir())
            self.assertEqual(first.name, "2026.4.25-1")
            self.assertEqual(second.name, "2026.4.25-2")

    def test_prepare_batch_directory_retries_on_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            (output_root / "2026.4.25-1").mkdir()
            (output_root / "2026.4.25-2").mkdir()

            created = MODULE.prepare_batch_directory(
                output_root, timestamp="2026.4.25", label=""
            )
            self.assertEqual(created.name, "2026.4.25-3")
            self.assertTrue(created.is_dir())

    def test_prepare_batch_directory_handles_racy_file_exists_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            call_counter = {"value": 0}
            original_mkdir = Path.mkdir

            def flaky_mkdir(path_obj, *args, **kwargs):
                if path_obj == output_root / "2026.4.25-1":
                    call_counter["value"] += 1
                    if call_counter["value"] == 1:
                        raise FileExistsError("simulated race")
                return original_mkdir(path_obj, *args, **kwargs)

            with mock.patch.object(Path, "mkdir", autospec=True, side_effect=flaky_mkdir):
                created = MODULE.prepare_batch_directory(
                    output_root, timestamp="2026.4.25", label=""
                )
            self.assertEqual(created.name, "2026.4.25-2")
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

    def test_serialize_candidate_reads_file_fields_from_body_content(self) -> None:
        message = {
            "message_id": "m-file",
            "create_time": "1714000000001",
            "sender": {"name": "杨东东"},
            "body": {"content": '{"file_key":"fk_1","file_name":"paper.pdf"}'},
        }
        self.assertEqual(
            MODULE.serialize_candidate(message),
            {
                "message_id": "m-file",
                "file_key": "fk_1",
                "file_name": "paper.pdf",
                "sender_name": "杨东东",
                "create_time": "1714000000001",
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
        self.assertEqual(mocked_open.call_args.kwargs["timeout"], 30)

    def test_request_json_propagates_url_errors(self) -> None:
        with mock.patch.object(
            MODULE.urllib.request,
            "urlopen",
            side_effect=urllib.error.URLError("network down"),
        ):
            with self.assertRaises(urllib.error.URLError):
                MODULE.request_json("https://example.test/open-apis/ping")

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

    def test_fetch_tenant_access_token_raises_on_api_error_code(self) -> None:
        with mock.patch.object(
            MODULE,
            "send_json",
            return_value={"code": 99991663, "msg": "invalid app credential"},
        ):
            with self.assertRaisesRegex(RuntimeError, "invalid app credential"):
                MODULE.fetch_tenant_access_token("bad_id", "bad_secret")

    def test_fetch_tenant_access_token_uses_passed_api_base_and_timeout(self) -> None:
        with mock.patch.object(
            MODULE,
            "send_json",
            return_value={"code": 0, "tenant_access_token": "t-456"},
        ) as mocked_send_json:
            token = MODULE.fetch_tenant_access_token(
                "cli_id",
                "cli_secret",
                api_base="https://feishu.internal/open-apis",
                timeout=9,
            )
        self.assertEqual(token, "t-456")
        args = mocked_send_json.call_args.args
        kwargs = mocked_send_json.call_args.kwargs
        self.assertEqual(
            args[0],
            "https://feishu.internal/open-apis/auth/v3/tenant_access_token/internal",
        )
        self.assertEqual(kwargs["timeout"], 9)

    def test_feishu_client_constructor_uses_api_base_and_timeout_for_auth(self) -> None:
        with mock.patch.object(MODULE, "fetch_tenant_access_token", return_value="tenant-token") as mocked_fetch:
            client = MODULE.FeishuClient(
                "app_id",
                "app_secret",
                api_base="https://sandbox.feishu.cn/open-apis",
                timeout=17,
            )
        self.assertEqual(client.tenant_access_token, "tenant-token")
        mocked_fetch.assert_called_once_with(
            "app_id",
            "app_secret",
            api_base="https://sandbox.feishu.cn/open-apis",
            timeout=17,
        )

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
            side_effect=[
                {
                    "code": 0,
                    "data": {
                        "items": [
                            {
                                "message_id": "m-1",
                                "msg_type": "file",
                                "create_time": "1714000000100",
                                "sender": {"id": "ou_yang", "id_type": "open_id"},
                                "body": {"content": '{"file_key":"fk-1","file_name":"ok.pdf"}'},
                            },
                            {
                                "message_id": "m-2",
                                "msg_type": "text",
                                "create_time": "1714000000200",
                                "sender": {"id": "ou_yang", "id_type": "open_id"},
                                "body": {"content": '{"text":"hi"}'},
                            },
                        ],
                        "has_more": False,
                        "page_token": "",
                    },
                }
            ],
        ) as mocked_request_json, mock.patch.object(MODULE.time, "time", return_value=1714000000.2):
            items = client.list_recent_files(
                chat_id="oc_test_chat",
                sender_name="",
                sender_open_id="ou_yang",
                hours=1,
            )
        self.assertEqual([item["message_id"] for item in items], ["m-1"])
        request_kwargs = mocked_request_json.call_args.kwargs
        self.assertEqual(request_kwargs["method"], "GET")
        self.assertIn("/im/v1/messages?", request_kwargs["url"])
        self.assertIn("container_id=oc_test_chat", request_kwargs["url"])
        self.assertIn("page_size=50", request_kwargs["url"])
        self.assertEqual(
            request_kwargs["headers"]["Authorization"],
            "Bearer tenant-token",
        )

    def test_feishu_client_resolves_sender_open_id_from_chat_members(self) -> None:
        with mock.patch.object(MODULE, "fetch_tenant_access_token", return_value="tenant-token"):
            client = MODULE.FeishuClient("app_id", "app_secret")
        with mock.patch.object(
            MODULE,
            "request_json",
            return_value={
                "code": 0,
                "data": {
                    "items": [
                        {"member_id": "ou_other", "name": "Nezikk"},
                        {"member_id": "ou_yang", "name": "杨东东"},
                    ],
                    "has_more": False,
                    "page_token": "",
                },
            },
        ) as mocked_request_json:
            sender_open_id = client.resolve_sender_open_id(
                "oc_test_chat",
                sender_name="杨东东",
                sender_open_id="",
            )
        self.assertEqual(sender_open_id, "ou_yang")
        self.assertIn("/im/v1/chats/oc_test_chat/members", mocked_request_json.call_args.kwargs["url"])

    def test_feishu_client_list_recent_files_follows_pagination(self) -> None:
        with mock.patch.object(MODULE, "fetch_tenant_access_token", return_value="tenant-token"):
            client = MODULE.FeishuClient("app_id", "app_secret")
        first_page = {
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
                    }
                ],
                "has_more": True,
                "page_token": "next_1",
            },
        }
        second_page = {
            "code": 0,
            "data": {
                "items": [
                    {
                        "message_id": "m-2",
                        "message_type": "file",
                        "create_time": "1714000000200",
                        "sender": {
                            "sender_name": "Yang",
                            "sender_id": {"open_id": "ou_yang"},
                        },
                        "body": {"file_key": "fk-2", "file_name": "ok-2.pdf"},
                    }
                ],
                "has_more": False,
                "page_token": "",
            },
        }
        with mock.patch.object(
            MODULE,
            "request_json",
            side_effect=[first_page, second_page],
        ) as mocked_request_json, mock.patch.object(MODULE.time, "time", return_value=1714000000.2):
            items = client.list_recent_files(
                chat_id="oc_test_chat",
                sender_name="Yang",
                sender_open_id="ou_yang",
                hours=1,
            )
        self.assertEqual([item["message_id"] for item in items], ["m-1", "m-2"])
        first_url = mocked_request_json.call_args_list[0].kwargs["url"]
        second_url = mocked_request_json.call_args_list[1].kwargs["url"]
        self.assertNotIn("page_token=", first_url)
        self.assertIn("page_token=next_1", second_url)

    def test_feishu_client_list_recent_files_raises_on_api_error(self) -> None:
        with mock.patch.object(MODULE, "fetch_tenant_access_token", return_value="tenant-token"):
            client = MODULE.FeishuClient("app_id", "app_secret")
        with mock.patch.object(
            MODULE,
            "request_json",
            return_value={"code": 10016, "msg": "permission denied"},
        ):
            with self.assertRaisesRegex(RuntimeError, "permission denied"):
                client.list_recent_files(
                    chat_id="oc_test_chat",
                    sender_name="Yang",
                    sender_open_id="ou_yang",
                    hours=1,
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

    def test_feishu_client_send_file_message_raises_on_api_error(self) -> None:
        with mock.patch.object(MODULE, "fetch_tenant_access_token", return_value="tenant-token"):
            client = MODULE.FeishuClient("app_id", "app_secret")
        with mock.patch.object(
            MODULE,
            "send_json",
            return_value={"code": 10016, "msg": "permission denied"},
        ):
            with self.assertRaisesRegex(RuntimeError, "permission denied"):
                client.send_file_message("oc_chat_1", "file_key_1")


class FeishuYangCliCommandTests(unittest.TestCase):
    def test_main_send_file_requires_path(self) -> None:
        argv = ["feishu_yang_cli", "send-file"]
        with mock.patch.object(sys, "argv", argv), mock.patch("sys.stderr", new_callable=io.StringIO) as stderr:
            with self.assertRaises(SystemExit) as exc:
                MODULE.main()
        self.assertEqual(exc.exception.code, 2)
        self.assertIn("--path", stderr.getvalue())

    def test_main_dispatches_send_file_command(self) -> None:
        argv = ["feishu_yang_cli", "send-file", "--path", "/tmp/mock.pdf"]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(
            MODULE, "run_send_file", return_value=0, create=True
        ) as mocked_handler:
            result = MODULE.main()
        self.assertEqual(result, 0)
        mocked_handler.assert_called_once()

    def test_main_dispatches_download_files_command(self) -> None:
        argv = ["feishu_yang_cli", "download-files", "--message-id", "om_1", "--hours", "48"]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(
            MODULE, "run_download_files", return_value=0, create=True
        ) as mocked_handler:
            result = MODULE.main()
        self.assertEqual(result, 0)
        mocked_handler.assert_called_once()

    def test_list_recent_files_json_execution_uses_mocked_client(self) -> None:
        argv = ["feishu_yang_cli", "list-recent-files", "--hours", "12", "--json"]
        env = {
            "FEISHU_APP_ID": "cli-id",
            "FEISHU_APP_SECRET": "cli-secret",
            "FEISHU_YANG_CHAT_ID": "oc_chat_1",
            "FEISHU_YANG_SENDER_NAME": "Yang",
            "FEISHU_YANG_SENDER_OPEN_ID": "ou_yang",
        }
        fake_messages = [
            {
                "message_id": "om_1",
                "body": {"file_key": "fk_1", "file_name": "paper.pdf"},
                "sender": {"sender_name": "Yang"},
                "create_time": "1714000000001",
            }
        ]
        expected = [
            {
                "message_id": "om_1",
                "file_key": "fk_1",
                "file_name": "paper.pdf",
                "sender_name": "Yang",
                "create_time": "1714000000001",
            }
        ]

        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(
            sys, "argv", argv
        ), mock.patch.object(MODULE, "FeishuClient") as mocked_client_cls, mock.patch(
            "sys.stdout", new_callable=io.StringIO
        ) as stdout:
            mocked_client = mocked_client_cls.return_value
            mocked_client.list_recent_files.return_value = fake_messages
            result = MODULE.main()

        self.assertEqual(result, 0)
        self.assertEqual(json.loads(stdout.getvalue()), expected)
        mocked_client_cls.assert_called_once_with("cli-id", "cli-secret")
        mocked_client.list_recent_files.assert_called_once_with(
            chat_id="oc_chat_1",
            sender_name="Yang",
            sender_open_id="ou_yang",
            hours=12,
        )

    def test_build_client_from_settings_rejects_non_integer_timeout(self) -> None:
        settings = {
            "FEISHU_APP_ID": "app_id",
            "FEISHU_APP_SECRET": "app_secret",
            "FEISHU_YANG_CHAT_ID": "oc_chat",
            "FEISHU_HTTP_TIMEOUT": "abc",
        }
        with mock.patch.object(MODULE, "FeishuClient") as mocked_client_cls:
            with self.assertRaisesRegex(RuntimeError, "must be an integer"):
                MODULE.build_client_from_settings(settings)
        mocked_client_cls.assert_not_called()

    def test_build_client_from_settings_rejects_non_positive_timeout(self) -> None:
        settings = {
            "FEISHU_APP_ID": "app_id",
            "FEISHU_APP_SECRET": "app_secret",
            "FEISHU_YANG_CHAT_ID": "oc_chat",
            "FEISHU_HTTP_TIMEOUT": "0",
        }
        with mock.patch.object(MODULE, "FeishuClient") as mocked_client_cls:
            with self.assertRaisesRegex(RuntimeError, "must be > 0"):
                MODULE.build_client_from_settings(settings)
        mocked_client_cls.assert_not_called()

    def test_run_send_file_raises_when_file_missing(self) -> None:
        args = argparse.Namespace(path="/path/does/not/exist.pdf")
        with self.assertRaisesRegex(RuntimeError, "File not found"):
            MODULE.run_send_file(args)

    def test_run_send_file_propagates_runtime_error_from_client(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "input.pdf"
            source_path.write_bytes(b"data")
            args = argparse.Namespace(path=str(source_path))
            settings = {
                "FEISHU_APP_ID": "app_id",
                "FEISHU_APP_SECRET": "app_secret",
                "FEISHU_YANG_CHAT_ID": "oc_chat",
                "FEISHU_YANG_SENDER_NAME": "",
                "FEISHU_YANG_SENDER_OPEN_ID": "",
                "FEISHU_API_BASE": "",
                "FEISHU_HTTP_TIMEOUT": "",
            }
            with mock.patch.object(MODULE, "load_runtime_settings", return_value=settings), mock.patch.object(
                MODULE, "build_client_from_settings"
            ) as mocked_builder:
                mocked_client = mocked_builder.return_value
                mocked_client.upload_file.side_effect = RuntimeError("upload failed")
                with self.assertRaisesRegex(RuntimeError, "upload failed"):
                    MODULE.run_send_file(args)

    def test_run_download_files_success_uses_hours_and_downloads_message_ids(self) -> None:
        args = argparse.Namespace(
            message_ids=["om_1", "om_2"],
            output_root="/tmp/yang-downloads",
            hours=72,
        )
        settings = {
            "FEISHU_APP_ID": "app_id",
            "FEISHU_APP_SECRET": "app_secret",
            "FEISHU_YANG_CHAT_ID": "oc_chat",
            "FEISHU_YANG_SENDER_NAME": "Yang",
            "FEISHU_YANG_SENDER_OPEN_ID": "ou_yang",
            "FEISHU_API_BASE": "",
            "FEISHU_HTTP_TIMEOUT": "",
        }
        recent_messages = [
            {
                "message_id": "om_1",
                "body": {"file_key": "fk_1", "file_name": "a.pdf"},
            },
            {
                "message_id": "om_2",
                "body": {"file_key": "fk_2", "file_name": "b.pdf"},
            },
        ]

        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            MODULE, "load_runtime_settings", return_value=settings
        ), mock.patch.object(MODULE, "build_client_from_settings") as mocked_builder, mock.patch.object(
            MODULE, "prepare_batch_directory", return_value=Path(tmp) / "batch"
        ) as mocked_batch, mock.patch(
            "sys.stdout", new_callable=io.StringIO
        ) as stdout:
            batch_dir = Path(tmp) / "batch"
            batch_dir.mkdir(parents=True, exist_ok=True)
            mocked_client = mocked_builder.return_value
            mocked_client.list_recent_files.return_value = recent_messages
            result = MODULE.run_download_files(args)

        self.assertEqual(result, 0)
        mocked_client.list_recent_files.assert_called_once_with(
            chat_id="oc_chat",
            sender_name="Yang",
            sender_open_id="ou_yang",
            hours=72,
        )
        mocked_batch.assert_called_once()
        self.assertEqual(mocked_client.download_file.call_count, 2)
        self.assertIn('"message_id": "om_1"', stdout.getvalue())
        self.assertIn('"message_id": "om_2"', stdout.getvalue())

    def test_run_download_files_raises_when_message_id_not_in_recent_files(self) -> None:
        args = argparse.Namespace(
            message_ids=["om_missing"],
            output_root="/tmp/yang-downloads",
            hours=24,
        )
        settings = {
            "FEISHU_APP_ID": "app_id",
            "FEISHU_APP_SECRET": "app_secret",
            "FEISHU_YANG_CHAT_ID": "oc_chat",
            "FEISHU_YANG_SENDER_NAME": "Yang",
            "FEISHU_YANG_SENDER_OPEN_ID": "ou_yang",
            "FEISHU_API_BASE": "",
            "FEISHU_HTTP_TIMEOUT": "",
        }
        with mock.patch.object(MODULE, "load_runtime_settings", return_value=settings), mock.patch.object(
            MODULE, "build_client_from_settings"
        ) as mocked_builder:
            mocked_client = mocked_builder.return_value
            mocked_client.list_recent_files.return_value = []
            with self.assertRaisesRegex(RuntimeError, "Message IDs not found"):
                MODULE.run_download_files(args)


if __name__ == "__main__":
    unittest.main()
