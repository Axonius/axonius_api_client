# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import pytest
from click.testing import CliRunner

from axonius_api_client import cli, connect, tools

from .. import utils


def to_json(ctx, raw_data, **kwargs):
    """Pass."""
    return tools.json_dump(obj=raw_data, **kwargs)


class TestCliExcWrap(object):
    """Pass."""

    def test_exc_wrap_true(self, capsys):
        """Pass."""
        with pytest.raises(SystemExit):
            with cli.context.Context.exc_wrap(wraperror=True):
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
            with cli.context.Context.exc_wrap(wraperror=False):
                raise utils.MockError("badwolf")


class TestCliContext(object):
    """Pass."""

    def test_init(self):
        """Pass."""
        obj = cli.context.Context()
        assert format(obj)
        assert repr(obj)
        assert obj.wraperror is True

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

    def test_start_client(self, request):
        """Pass."""
        obj = cli.context.Context()
        url = request.config.getoption("--ax-url")
        key = request.config.getoption("--ax-key")
        secret = request.config.getoption("--ax-secret")
        assert obj.client is None
        client = obj.start_client(url=url, key=key, secret=secret)
        assert isinstance(client, connect.Connect)
        assert client == obj.client

    def test_handle_export(self, capsys):
        """Pass."""
        obj = cli.context.Context()
        obj.handle_export(
            raw_data={},
            formatters={"json": to_json},
            export_format="json",
            export_file=None,
            export_path=None,
            export_overwrite=False,
        )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert not stderr

        stdout = captured.out.splitlines()
        assert len(stdout) == 1

        assert stdout[0] == "{}"

    def test_handle_export_invalid(self, capsys):
        """Pass."""
        obj = cli.context.Context()
        with pytest.raises(SystemExit):
            obj.handle_export(
                raw_data={},
                formatters={"json": to_json},
                export_format="jsox",
                export_file=None,
                export_path=None,
                export_overwrite=False,
            )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 1

        stdout = captured.out.splitlines()
        assert not stdout

        exp0 = "** ERROR: Export format {!r} is unsupported".format("jsox")
        assert stderr[0].startswith(exp0)
