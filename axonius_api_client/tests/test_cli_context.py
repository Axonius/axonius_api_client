# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import pdb  # noqa

import pytest
from click.testing import CliRunner

from axonius_api_client import cli

from . import utils


class TestCliRegisterReadline(object):
    """Pass."""

    def test_default(self):
        """Pass."""
        cli.context.register_readline()

    def test_exc(self, monkeypatch, capsys):
        """Pass."""
        monkeypatch.setattr(cli.context, "readline", utils.MockError)
        cli.context.register_readline()
        captured = capsys.readouterr()
        assert (
            captured.err.splitlines()[0]
            == "** ERROR: Unable to register history and autocomplete:"
        )


class TestCliLoadEnv(object):
    """Pass."""

    def test_axenv(self, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            with open("test.env", "w") as f:
                f.write("AX_TEST=badwolf1\n")
            monkeypatch.delenv("AX_TEST", raising=False)
            monkeypatch.setenv("AX_ENV", "test.env")
            cli.context.load_dotenv()
            assert os.environ["AX_TEST"] == "badwolf1"

    def test_default(self, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            with open(".env", "w") as f:
                f.write("AX_TEST=badwolf2\n")
            monkeypatch.delenv("AX_TEST", raising=False)
            monkeypatch.delenv("AX_ENV", raising=False)
            cli.context.load_dotenv()
            assert os.environ["AX_TEST"] == "badwolf2"


class TestCliContext(object):
    """Pass."""

    def test_init(self):
        """Pass."""
        obj = cli.context.Context()
        assert format(obj)
        assert repr(obj)

    def test_export_stdout(self, capsys):
        """Pass."""
        obj = cli.context.Context()
        obj.export(data="badwolf")
        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert not stderr

        stdout = captured.out.splitlines()
        assert len(stdout) == 1

        assert stdout[0] == "badwolf"

    def test_export_file(self, capsys):
        """Pass."""
        runner = CliRunner(mix_stderr=False)
        obj = cli.context.Context()

        with runner.isolated_filesystem():
            obj.export(data="badwolf", export_file="badwolf.test")
            assert os.path.isfile("badwolf.test")

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 1

        stdout = captured.out.splitlines()
        assert not stdout

        assert stderr[0].startswith("** Exported file")
        assert "created" in stderr[0]

    def test_export_file_exists(self, capsys):
        """Pass."""
        runner = CliRunner(mix_stderr=False)
        obj = cli.context.Context()

        with runner.isolated_filesystem():
            with open("badwolf.test", "w") as f:
                f.write("badwolf")

            with pytest.raises(SystemExit):
                obj.export(data="badwolf", export_file="badwolf.test")

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 1

        stdout = captured.out.splitlines()
        assert not stdout

        assert stderr[0].startswith("** ERROR: Export file")

    def test_export_file_overwrite(self, capsys):
        """Pass."""
        runner = CliRunner(mix_stderr=False)
        obj = cli.context.Context()

        with runner.isolated_filesystem():
            with open("badwolf.test", "w") as f:
                f.write("badwolf1")

            obj.export(
                data="badwolf2", export_file="badwolf.test", export_overwrite=True
            )
            assert os.path.isfile("badwolf.test")
            with open("badwolf.test", "r") as f:
                assert f.read() == "badwolf2"

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 1

        stdout = captured.out.splitlines()
        assert not stdout

        assert stderr[0].startswith("** Exported file")
        assert "overwritten" in stderr[0]

    def test_echo_ok(self, capsys):
        """Pass."""
        cli.context.Context.echo_ok("badwolf")

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 1

        stdout = captured.out.splitlines()
        assert not stdout

        assert stderr[0] == "** badwolf"

    def test_echo_warn(self, capsys):
        """Pass."""
        cli.context.Context.echo_warn("badwolf")

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 1

        stdout = captured.out.splitlines()
        assert not stdout

        assert stderr[0] == "** WARNING: badwolf"

    def test_echo_error_abort(self, capsys):
        """Pass."""
        with pytest.raises(SystemExit):
            cli.context.Context.echo_error("badwolf", abort=True)

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 1

        stdout = captured.out.splitlines()
        assert not stdout

        assert stderr[0] == "** ERROR: badwolf"

    def test_echo_error_noabort(self, capsys):
        """Pass."""
        cli.context.Context.echo_error("badwolf", abort=False)

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 1

        stdout = captured.out.splitlines()
        assert not stdout

        assert stderr[0] == "** ERROR: badwolf"

    def test_exc_wrap_true(self, capsys):
        """Pass."""
        with pytest.raises(SystemExit):
            with cli.context.exc_wrap(wraperror=True):
                raise utils.MockError("badwolf")

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 2

        stdout = captured.out.splitlines()
        assert not stdout

        exp0 = "** ERROR: WRAPPED EXCEPTION: {c.__module__}.{c.__name__}"
        exp0 = exp0.format(c=utils.MockError)
        assert stderr[0] == exp0
        assert stderr[1] == "badwolf"

    def test_exc_wrap_false(self, capsys):
        """Pass."""
        with pytest.raises(utils.MockError):
            with cli.context.exc_wrap(wraperror=False):
                raise utils.MockError("badwolf")
