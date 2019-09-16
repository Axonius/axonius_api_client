# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import pytest
from click.testing import CliRunner

from axonius_api_client import cli, exceptions, tools

from .. import utils


class TestCmdShell(object):
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
                result1 = runner.invoke(cli=cli.cli, args=["shell"], input=prompt_input)

            assert histfile.is_file(), list(histpath.iterdir())

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        outlines1 = stdout1.splitlines()

        assert outlines1[0] == "URL of Axonius instance: {}".format(url)
        assert outlines1[1] == "API Key of user in Axonius instance: "
        assert outlines1[2] == "API Secret of user in Axonius instance: "

        utils.check_stderr_lines(result1)

    def test_no_prompt(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        prompt_input = "\n".join(["exit()"])

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            histfile = histpath / cli.context.HISTFILE
            monkeypatch.setattr(cli.context, "HISTPATH", format(histpath))

            with pytest.warns(exceptions.BetaWarning):
                result1 = runner.invoke(cli=cli.cli, args=["shell"], input=prompt_input)

            assert histfile.is_file(), list(histpath.iterdir())
        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        assert exit_code1 == 0

        utils.check_stderr_lines(result1)
