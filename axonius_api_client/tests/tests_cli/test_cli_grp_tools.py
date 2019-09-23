# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import pytest
from click.testing import CliRunner

from axonius_api_client import cli, tools

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
        prompt_input = "\n".join([url, key, secret, "exit()"])

        args = ["tools", "shell"]

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            histfile = histpath / cli.cli_constants.HISTFILE
            monkeypatch.setattr(cli.cli_constants, "HISTPATH", format(histpath))

            result1 = runner.invoke(cli=cli.cli, args=args, input=prompt_input)

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

    def test_no_prompt(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        prompt_input = "\n".join(["exit()"])

        args = ["tools", "shell"]

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            histfile = histpath / cli.cli_constants.HISTFILE
            monkeypatch.setattr(cli.cli_constants, "HISTPATH", format(histpath))

            result1 = runner.invoke(cli=cli.cli, args=args, input=prompt_input)

            assert histfile.is_file(), list(histpath.iterdir())
        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        assert exit_code1 == 0


class TestCliWriteHistFile(object):
    """Pass."""

    def test_default(self, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            histfile = histpath / cli.cli_constants.HISTFILE
            monkeypatch.setattr(cli.cli_constants, "HISTPATH", format(histpath))
            cli.grp_tools.cmd_shell.write_hist_file()
            assert histfile.is_file(), list(histpath.iterdir())


class TestCliRegisterReadline(object):
    """Pass."""

    def test_default(self, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            histfile = histpath / cli.cli_constants.HISTFILE
            monkeypatch.setattr(cli.cli_constants, "HISTPATH", format(histpath))

            cli.grp_tools.cmd_shell.register_readline()
            assert histfile.is_file(), list(histpath.iterdir())

    def test_exc(self, monkeypatch, capsys):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        with runner.isolated_filesystem():
            monkeypatch.setattr(cli.grp_tools.cmd_shell, "atexit", utils.MockError)

            histpath = tools.pathlib.Path(os.getcwd())
            histfile = histpath / cli.cli_constants.HISTFILE
            monkeypatch.setattr(cli.cli_constants, "HISTPATH", format(histpath))

            cli.grp_tools.cmd_shell.register_readline()

            assert histfile.is_file(), list(histpath.iterdir())

        captured = capsys.readouterr()

        assert (
            captured.err.splitlines()[0]
            == "** ERROR: Unable to register history and autocomplete:"
        )


class TestCliJdump(object):
    """Pass."""

    def test_default(self, capsys):
        """Pass."""
        cli.grp_tools.cmd_shell.jdump([])
        captured = capsys.readouterr()
        assert captured.out.splitlines()[0] == "[]"


class TestCliSpawnShell(object):
    """Pass."""

    def test_default(self, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        monkeypatch.setattr("sys.stdin", tools.six.StringIO("exit()"))

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            monkeypatch.setattr(cli.cli_constants, "HISTPATH", format(histpath))

            with pytest.raises(SystemExit):
                cli.grp_tools.cmd_shell.spawn_shell()


class TestCmdWriteConfig(object):
    """Pass."""

    def test_prompt(self, request, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        url = request.config.getoption("--ax-url")
        key = request.config.getoption("--ax-key")
        secret = request.config.getoption("--ax-secret")

        prompt_input = "\n".join([url, key, secret])

        args = ["tools", "write-config"]

        with runner.isolated_filesystem():
            path = tools.pathlib.Path(os.getcwd())
            envfile = path / ".env"
            result1 = runner.invoke(cli=cli.cli, args=args, input=prompt_input)
            assert envfile.is_file()

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0
