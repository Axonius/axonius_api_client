# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.tools import json_load

from ....cli import cli
from ...utils import load_clirunner


class TestGrpMetaCmdAbout:
    def test_export_json(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                "system",
                "meta",
                "about",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

    def test_export_str(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                "system",
                "meta",
                "about",
                "--export-format",
                "str",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
