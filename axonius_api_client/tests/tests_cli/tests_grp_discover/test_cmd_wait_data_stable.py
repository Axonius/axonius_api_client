# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli

from ...utils import load_clirunner


class TestGrpDiscoverCmdWaitDataStable:
    def test_stop_wait(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli=cli,
                args=[
                    "system",
                    "discover",
                    "stop",
                ],
            )

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            result = runner.invoke(
                cli=cli,
                args=[
                    "system",
                    "discover",
                    "wait-data-stable",
                ],
            )

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
