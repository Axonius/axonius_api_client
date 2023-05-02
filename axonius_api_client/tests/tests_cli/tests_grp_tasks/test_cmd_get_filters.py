# -*- coding: utf-8 -*-
"""Tests for axonshell enforcements tasks get-filters."""
from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load
from ...utils import load_clirunner


class TestGrpTasksCmdGetFilters:
    def test_json_export(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "tasks",
                "get-filters",
                "--export-format",
                "json",
                "--no-include-discovery-uuids",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            data = json_load(result.stdout)
            assert isinstance(data, dict)

    def test_str_export(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "tasks",
                "get-filters",
                "--export-format",
                "str",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

    def test_json_file_export(self, request, monkeypatch, tmp_path):
        path = tmp_path / "test.json"
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "tasks",
                "get-filters",
                "--export-format",
                "json",
                "--export-file",
                f"{path}",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code == 0
            data = json_load(path)
            assert isinstance(data, dict)
