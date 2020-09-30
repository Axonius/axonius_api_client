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

        args = ["tools", "write-config"]

        with runner.isolated_filesystem():
            path = pathlib.Path(os.getcwd())
            envfile = path / ".env"
            result1 = runner.invoke(cli=cli, args=args, input=prompt_input)
            assert envfile.is_file()

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0
