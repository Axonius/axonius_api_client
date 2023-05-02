# -*- coding: utf-8 -*-
"""Tests for axonshell enforcements tasks get."""
from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load
from ...utils import load_clirunner


class TestGrpTasksCmdGet:
    def test_json_export(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = ["enforcements", "tasks", "get", "--export-format", "json", "--row-stop", "1"]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            data = json_load(result.stdout)
            assert isinstance(data, list)
            for item in data:
                assert isinstance(item, dict)

    def test_jsonl_export(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = ["enforcements", "tasks", "get", "--export-format", "jsonl", "--row-stop", "1"]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            data = [json_load(x.strip()) for x in result.stdout.splitlines() if x.strip()]
            assert isinstance(data, list)
            for item in data:
                assert isinstance(item, dict)

    def test_str_export(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = ["enforcements", "tasks", "get", "--export-format", "str", "--row-stop", "1"]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

    def test_csv_export(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = ["enforcements", "tasks", "get", "--export-format", "csv", "--row-stop", "1"]
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
                "get",
                "--export-format",
                "json",
                "--export-file",
                f"{path}",
                "--row-stop",
                "1",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code == 0
            data = json_load(path)
            assert isinstance(data, list)
