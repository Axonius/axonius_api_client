# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""

from click.testing import CliRunner

from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load


class TestCmdSysInfo(object):
    def test_get_str(self, request, monkeypatch):
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            args = ["tools", "sysinfo", "--export-format", "str"]

            result1 = runner.invoke(cli=cli, args=args)
            assert result1.stdout
            assert not result1.stderr

    def test_get_json(self, request, monkeypatch):
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            args = ["tools", "sysinfo", "--export-format", "json"]

            result1 = runner.invoke(cli=cli, args=args)
            assert result1.stdout
            assert not result1.stderr
            json1 = json_load(result1.stdout)
            assert isinstance(json1, dict) and json1
