# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load

from ...utils import load_clirunner


class TestGrpSavedQueryCmdGetQueryHistory:
    @pytest.mark.parametrize("export_format", ["json"])
    def test_json_exports(self, request, monkeypatch, export_format):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args1 = [
                "devices",
                "saved-query",
                "get-query-history",
                "--export-format",
                export_format,
            ]
            result1 = runner.invoke(cli=cli, args=args1)

            assert result1.stdout
            assert result1.stderr
            assert result1.exit_code == 0

            json1 = json_load(result1.stdout)
            assert isinstance(json1, list) and json1
            for item in json1:
                assert isinstance(item, dict) and item

    @pytest.mark.parametrize("export_format", ["csv", "table"])
    def test_str_exports(self, request, monkeypatch, export_format):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args1 = [
                "devices",
                "saved-query",
                "get-query-history",
                "--export-format",
                export_format,
            ]
            result1 = runner.invoke(cli=cli, args=args1)

            assert result1.stdout
            assert result1.stderr
            assert result1.exit_code == 0
