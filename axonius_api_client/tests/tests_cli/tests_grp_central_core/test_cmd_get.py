# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load

from ...utils import load_clirunner


class TestGrpCentralCoreCmdGet:
    def test_get(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "system",
                "central-core",
                "get",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            data = json_load(result.stdout)
            assert isinstance(data, dict) and data
