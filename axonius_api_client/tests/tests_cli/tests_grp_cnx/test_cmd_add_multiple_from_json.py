# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from axonius_api_client.cli import cli
from axonius_api_client.tools import json_dump

from ...tests_api.tests_adapters.test_cnx import skip_if_no_adapter
from ...utils import load_clirunner
from .test_cnx_base import CnxTools

ERRORS = {
    "": ["Empty content supplied to '<stdin>'"],
    "{}": ["supplied is <class 'dict'>, required type is <class 'list'>"],
    "[]": ["Must supply at least 1 items, but only 0 items supplied"],
    "1": ["supplied is <class 'int'>, required type is <class 'list'>"],
    "[{}]": [
        "Connection item #1/1 initial parsing errors:",
        "'adapter_name' key is required but was not supplied",
        "'config' key is required but was not supplied",
        "'adapter_name' with value None type <class 'NoneType'> is not a <class 'str'> or is empty",
        "'config' with value None type <class 'NoneType'> is not a <class 'dict'> or is empty",
    ],
    '[{"adapter_name": "xx"}]': [
        "Connection item #1/1 initial parsing errors:",
        "'config' key is required but was not supplied",
        "'config' with value None type <class 'NoneType'> is not a <class 'dict'> or is empty",
    ],
    '[{"adapter": 111, "config": [], "save_and_fetch": "bad", "active": "foot"}]': [
        "Connection item #1/1 initial parsing errors:",
        "'active' is not a valid bool",
        "'save_and_fetch' is not a valid bool",
        "'adapter_name' with value 111 type <class 'int'> is not a <class 'str'> or is empty",
        "'config' with value [] type <class 'list'> is not a <class 'dict'> or is empty",
    ],
    '[{"adapter_name": "banzarbar", "config": {"x": "y"}}]': [
        "No adapter named 'banzarbar' found on instance",
    ],
}


class TestGrpCnxCmdAddMultipleFromJson(CnxTools):
    @pytest.mark.parametrize("content", list(ERRORS))
    def test_errors(self, api_adapters, request, content, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "adapters",
                "cnx",
                "add-multiple-from-json",
            ]

            result = runner.invoke(cli=cli, args=args, input=content)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code == 1

            for exp in ERRORS[content]:
                assert exp in result.stderr

    def test_errors_ignore_bad_adapter(self, api_adapters, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            content = '[{"adapter_name": "banzarbar", "config": {"x": "y"}}]'
            exps = [
                "No adapter named 'banzarbar' found on instance",
                "Added 0 out of 1 connections (error count: 1)",
            ]
            args = [
                "adapters",
                "cnx",
                "add-multiple-from-json",
                "--no-abort",
            ]

            result = runner.invoke(cli=cli, args=args, input=content)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code == 100

            for exp in exps:
                assert exp in result.stderr

    def test_errors_no_abort(self, api_adapters, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            content = "[{}, {}]"
            exps = [
                "ERROR: Connection item #1/2 Stopped processing! supplied:",
                "ERROR: Connection item #2/2 Stopped processing! supplied:",
                "Added 0 out of 2 connections (error count: 2)",
            ]
            args = [
                "adapters",
                "cnx",
                "add-multiple-from-json",
                "--no-abort",
            ]

            result = runner.invoke(cli=cli, args=args, input=content)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code == 100

            for exp in exps:
                assert exp in result.stderr

    def test_errors_unknown_config(self, api_adapters, request, monkeypatch):
        skip_if_no_adapter(api_adapters, "tanium")
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            content = '[{"adapter_name": "tanium", "config": {"x": "y"}}]'
            exps = [
                "Unknown config keys supplied:",
                "  x: 'y'",
                "Added 0 out of 1 connections (error count: 1)",
            ]
            args = [
                "adapters",
                "cnx",
                "add-multiple-from-json",
                "--no-abort",
            ]

            result = runner.invoke(cli=cli, args=args, input=content)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code == 100

            for exp in exps:
                assert exp in result.stderr

    def test_errors_ignore_unknown_config(self, api_adapters, request, monkeypatch):
        skip_if_no_adapter(api_adapters, "tanium")
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            content = '[{"adapter_name": "tanium", "config": {"x": "y"}}]'
            exps = [
                "Unknown config keys supplied:",
                "  x: 'y'",
                "Error in Schema 'domain': Must supply value!",
                "Added 0 out of 1 connections (error count: 1)",
            ]
            args = [
                "adapters",
                "cnx",
                "add-multiple-from-json",
                "--no-abort",
                "--ignore-unknowns",
            ]

            result = runner.invoke(cli=cli, args=args, input=content)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code == 100

            for exp in exps:
                assert exp in result.stderr

    def test_errors_no_abort_add_error(self, api_adapters, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            content = '[{"adapter_name": "csv", "config": {"user_id": "badwolf"}}]'
            exps = [
                "Connection item #1/1 Connection added with error:",
                # "Error: Error - No way to find the resource from config.",
                "Added 1 out of 1 connections (error count: 1)",
            ]
            args = [
                "adapters",
                "cnx",
                "add-multiple-from-json",
                "--no-abort",
                "--export-format",
                "json",
            ]

            result = runner.invoke(cli=cli, args=args, input=content)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 100

            for exp in exps:
                assert exp in result.stderr

            self.delete_cnx_from_content(runner=runner, content=result.stdout)

    def test_add_success_file_from_str(self, api_adapters, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            file_path = """CONTENT:"name","mac_address","extra_field"
"why","01:37:53:9E:82:7C","foo1"
"cuz","01:37:53:9E:82:8C","foo2"
"""
            content_obj = [
                {
                    "adapter_name": "csv",
                    "config": {"user_id": "badwolf from str", "file_path": file_path},
                }
            ]
            content = json_dump(content_obj)
            exps = [
                "Schema 'file_path': Resolved value to PosixPath",
                "Connection item #1/1 Connection added with no errors",
                "Added 1 out of 1 connections (error count: 0)",
            ]

            args = [
                "adapters",
                "cnx",
                "add-multiple-from-json",
                "--export-format",
                "json",
            ]

            result = runner.invoke(cli=cli, args=args, input=content)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            for exp in exps:
                assert exp in result.stderr

            self.delete_cnx_from_content(runner=runner, content=result.stdout)
