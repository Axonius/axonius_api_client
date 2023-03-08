# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli

from ...utils import load_clirunner


class TestGrpDiscoverCmdMulti:
    def check_is_running(self, runner, started: bool):
        with runner.isolated_filesystem():
            args = [
                "system",
                "discover",
                "is-running",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            if started:
                assert result.exit_code == 0
                assert "Is running: True" in result.stderr
            else:
                assert result.exit_code == 1
                assert "Is running: False" in result.stderr

    def check_is_stable(self, runner, started: bool):
        with runner.isolated_filesystem():
            args = [
                "system",
                "discover",
                "is-data-stable",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            if started:
                assert result.exit_code == 0
                assert "Data is stable: False" in result.stderr
            else:
                assert result.exit_code == 1
                assert "Data is stable: True" in result.stderr

    def check_result(self, result):
        assert result.stdout
        assert result.stderr
        assert result.exit_code == 0

    def test_multi(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            start_args = ["system", "discover", "start"]
            start_result = runner.invoke(cli=cli, args=start_args)
            self.check_result(result=start_result)

            self.check_is_running(runner=runner, started=True)
            self.check_is_stable(runner=runner, started=True)

            stop_args = ["system", "discover", "stop"]
            stop_result = runner.invoke(cli=cli, args=stop_args)
            self.check_result(result=stop_result)

            self.check_is_running(runner=runner, started=False)
            self.check_is_stable(runner=runner, started=False)
