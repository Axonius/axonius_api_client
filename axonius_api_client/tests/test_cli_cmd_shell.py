# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import pytest
from click.testing import CliRunner

from axonius_api_client import cli, exceptions, tools

from . import utils


class TestCliShell(object):
    """Pass."""

    def test_prompt(self, request, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        url = request.config.getoption("--ax-url")
        key = request.config.getoption("--ax-key")
        secret = request.config.getoption("--ax-secret")

        monkeypatch.delenv("AX_URL", raising=False)
        monkeypatch.delenv("AX_KEY", raising=False)
        monkeypatch.delenv("AX_SECRET", raising=False)
        monkeypatch.setattr(cli.context, "load_dotenv", utils.mock_load_dotenv)
        prompt_input = "\n".join([url, key, secret, "exit()"])

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            histfile = histpath / cli.context.HISTFILE
            monkeypatch.setattr(cli.context, "HISTPATH", format(histpath))

            with pytest.warns(exceptions.BetaWarning):
                result = runner.invoke(cli=cli.cli, args=["shell"], input=prompt_input)

            assert histfile.is_file(), list(histpath.iterdir())

        assert result.exit_code == 0

        stdout = result.stdout.splitlines()

        assert stdout[0] == "URL of Axonius instance: {}".format(url), stdout
        assert stdout[1] == "API Key of user in Axonius instance: ", stdout
        assert stdout[2] == "API Secret of user in Axonius instance: ", stdout

        utils.check_stderr_lines(result)

    def test_no_prompt(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        prompt_input = "\n".join(["exit()"])

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            histfile = histpath / cli.context.HISTFILE
            monkeypatch.setattr(cli.context, "HISTPATH", format(histpath))

            with pytest.warns(exceptions.BetaWarning):
                result = runner.invoke(cli=cli.cli, args=["shell"], input=prompt_input)

            assert histfile.is_file(), list(histpath.iterdir())

        assert result.exit_code == 0

        utils.check_stderr_lines(result)
