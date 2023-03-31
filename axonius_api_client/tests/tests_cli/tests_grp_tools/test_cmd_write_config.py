# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import os

from click.testing import CliRunner

from ....cli import cli
from ....tools import pathlib


class TestCmdWriteConfig(object):
    def test_prompt(self, request, monkeypatch):
        runner = CliRunner(mix_stderr=False)

        url = request.config.getoption("--ax-url")
        key = request.config.getoption("--ax-key")
        secret = request.config.getoption("--ax-secret")

        prompt_input = "\n".join([url, key, secret])

        with runner.isolated_filesystem():
            path = pathlib.Path(os.getcwd())
            envfile = path / ".env"
            args = ["tools", "write-config", "--env", f"{envfile}"]
            result1 = runner.invoke(cli=cli, args=args, input=prompt_input)
            assert envfile.is_file()
            assert not result1.stdout
            assert result1.stderr
            assert "Creating file" in result1.stderr
            assert result1.exit_code == 0

            result2 = runner.invoke(cli=cli, args=args, input=prompt_input)
            assert envfile.is_file()
            assert not result2.stdout
            assert result2.stderr
            assert "Updating file" in result2.stderr
            assert result2.exit_code == 0
