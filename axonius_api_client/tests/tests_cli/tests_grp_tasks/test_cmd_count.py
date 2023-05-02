# -*- coding: utf-8 -*-
"""Tests for axonshell enforcements tasks count."""
from axonius_api_client.cli import cli
from ...utils import load_clirunner


class TestGrpTasksCmdCount:
    def test_default(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "tasks",
                "count",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
