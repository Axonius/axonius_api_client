# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import io
import os

import pytest
from click.testing import CliRunner

from ....cli import cli
from ....cli.grp_tools import cmd_shell
from ....tools import pathlib
from ...utils import MockError, load_clirunner


class TestCmdShell:
    def test_prompt(self, request, monkeypatch):
        try:
            import readline  # noqa
        except Exception:
            pytest.skip("No readline support")

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
            histpath = pathlib.Path(os.getcwd())
            histfile = histpath / cmd_shell.HISTFILE
            monkeypatch.setattr(cmd_shell, "HISTPATH", format(histpath))

            result1 = runner.invoke(cli=cli, args=args, input=prompt_input)

            assert histfile.is_file(), list(histpath.iterdir())

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        outlines1 = stdout1.splitlines()

        assert outlines1[0] == "URL: {}".format(url)
        assert outlines1[1].startswith("API Key")
        assert outlines1[2].startswith("API Secret")

    def test_no_prompt(self, request, monkeypatch):
        try:
            import readline  # noqa
        except Exception:
            pytest.skip("No readline support")

        runner = load_clirunner(request, monkeypatch)

        prompt_input = "\n".join(["exit()"])

        args = ["tools", "shell"]

        with runner.isolated_filesystem():
            histpath = pathlib.Path(os.getcwd())
            histfile = histpath / cmd_shell.HISTFILE
            monkeypatch.setattr(cmd_shell, "HISTPATH", format(histpath))

            result1 = runner.invoke(cli=cli, args=args, input=prompt_input)

            assert histfile.is_file(), list(histpath.iterdir())
        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        assert exit_code1 == 0


class TestCliWriteHistFile:
    def test_default(self, monkeypatch):
        try:
            import readline  # noqa
        except Exception:
            pytest.skip("No readline support")

        runner = CliRunner(mix_stderr=False)

        with runner.isolated_filesystem():
            histpath = pathlib.Path(os.getcwd())
            histfile = histpath / cmd_shell.HISTFILE
            monkeypatch.setattr(cmd_shell, "HISTPATH", format(histpath))
            cmd_shell.write_hist_file()
            assert histfile.is_file(), list(histpath.iterdir())


class TestCliRegisterReadline:
    def test_default(self, monkeypatch):
        try:
            import readline  # noqa
        except Exception:
            pytest.skip("No readline support")

        runner = CliRunner(mix_stderr=False)

        with runner.isolated_filesystem():
            histpath = pathlib.Path(os.getcwd())
            histfile = histpath / cmd_shell.HISTFILE
            monkeypatch.setattr(cmd_shell, "HISTPATH", format(histpath))

            cmd_shell.register_readline()
            assert histfile.is_file(), list(histpath.iterdir())

    def test_exc(self, monkeypatch, capsys):
        try:
            import readline  # noqa
        except Exception:
            pytest.skip("No readline support")
        runner = CliRunner(mix_stderr=False)

        with runner.isolated_filesystem():
            monkeypatch.setattr(cmd_shell, "atexit", MockError)

            histpath = pathlib.Path(os.getcwd())
            histfile = histpath / cmd_shell.HISTFILE
            monkeypatch.setattr(cmd_shell, "HISTPATH", format(histpath))

            cmd_shell.register_readline()

            assert histfile.is_file(), list(histpath.iterdir())

        captured = capsys.readouterr()

        assert (
            captured.err.splitlines()[0] == "** ERROR: Unable to register history and autocomplete:"
        )


class TestCliJdump:
    def test_default(self, capsys):
        cmd_shell.jdump([])
        captured = capsys.readouterr()
        assert captured.out.splitlines()[0] == "[]"


class TestCliSpawnShell:
    def test_default(self, monkeypatch):
        runner = CliRunner(mix_stderr=False)

        monkeypatch.setattr("sys.stdin", io.StringIO("exit()"))

        with runner.isolated_filesystem():
            histpath = pathlib.Path(os.getcwd())
            monkeypatch.setattr(cmd_shell, "HISTPATH", format(histpath))

            with pytest.raises(SystemExit):
                cmd_shell.spawn_shell()
