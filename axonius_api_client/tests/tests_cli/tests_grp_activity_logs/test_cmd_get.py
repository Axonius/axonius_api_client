# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load

from ...utils import load_clirunner


class TestGrpActivityLogsCmdGet:
    @pytest.mark.parametrize("export_format", ["json"])
    def test_json_exports(self, request, monkeypatch, export_format):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "system",
                "activity-logs",
                "get",
                "--export-format",
                export_format,
                "--max-rows",
                "2",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            data = json_load(result.stdout)
            assert isinstance(data, list) and len(data) <= 2
            for item in data:
                assert isinstance(item, dict)

    @pytest.mark.parametrize("export_format", ["str", "csv"])
    def test_str_exports(self, request, monkeypatch, export_format):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "system",
                "activity-logs",
                "get",
                "--export-format",
                export_format,
                "--max-rows",
                "2",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stderr
            assert result.stdout
            assert result.exit_code == 0
