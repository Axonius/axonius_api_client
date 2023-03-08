# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load

from ...tests_api.tests_enforcements.test_enforcements import EnforcementsBase
from ...utils import load_clirunner


class TestGrpEnforcementsCmdGet(EnforcementsBase):
    def test_json_export(self, request, monkeypatch, created_set):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "get",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert created_set.name in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, list) and data
            for x in data:
                assert isinstance(x, dict) and x

    @pytest.mark.parametrize("export_format", ["str", "table"])
    def test_str_exports(self, request, monkeypatch, created_set, export_format):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "get",
                "--export-format",
                export_format,
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert created_set.name in result.stdout

    def test_single_json_export(self, request, monkeypatch, created_set):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "get",
                "--value",
                created_set.name,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert created_set.name in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

    @pytest.mark.parametrize("export_format", ["str", "table"])
    def test_single_str_exports(self, request, monkeypatch, created_set, export_format):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "get",
                "--value",
                created_set.name,
                "--export-format",
                export_format,
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert created_set.name in result.stdout
