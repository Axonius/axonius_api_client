# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ....tools import json_load
from ...utils import load_clirunner


class TestGrpAdaptersCmdGet:
    def test_json_full(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get", "--export-format", "json-full"]
        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = json_load(stdout1)
        assert isinstance(json1, list)

    def test_json_basic(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get", "--export-format", "json"]
        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = json_load(stdout1)
        assert isinstance(json1, list)

    def test_table(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get", "--export-format", "table"]
        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

    def test_str(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get", "--export-format", "str"]
        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

    def test_str_args(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get", "--export-format", "str-args"]
        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0
