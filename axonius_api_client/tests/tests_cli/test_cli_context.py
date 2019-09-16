# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import pytest
from click.testing import CliRunner

from axonius_api_client import cli, connect, tools

from .. import utils


def badwolf_cb(x, **kwargs):
    """Pass."""
    return ["a", "b"]


def to_json(ctx, raw_data, **kwargs):
    """Pass."""
    return tools.json_dump(obj=raw_data, **kwargs)


class TestJoin(object):
    """Pass."""

    def test_kv(self):
        """Pass."""
        x = cli.context.join_kv({"a": "b", "c": "d"})
        assert x == "\n  a: b\n  c: d"

    def test_tv(self):
        """Pass."""
        x = cli.context.join_tv(
            {"a": {"title": "a", "value": 1}, "b": {"title": "b", "value": 2}}
        )
        assert x == "a: 1\nb: 2"

    def test_cr(self):
        """Pass."""
        x = cli.context.join_cr(["a", "b"])
        assert x == "a\nb"


class TestToJson(object):
    """Pass."""

    def test_default(self):
        """Pass."""
        x = cli.context.to_json(ctx=None, raw_data=[])
        assert x == "[]"


class TestCheckEmpty(object):
    """Pass."""

    @pytest.mark.parametrize("value", tools.EMPTY, scope="class")
    def test_empty_value(self, value):
        """Pass."""
        cli.context.check_empty(
            ctx=None,
            this_data=[],
            prev_data=[],
            value_type="badwolf",
            value=value,
            objtype="wolves",
            known_cb=None,
            known_cb_key="bad",
        )

    def test_empty_data(self, capsys):
        """Pass."""
        ctx = cli.context.Context()

        with pytest.raises(SystemExit):
            cli.context.check_empty(
                ctx=ctx,
                this_data=[],
                prev_data=[{"a": "1", "b": "2"}],
                value_type="badwolf",
                value=["d", "e"],
                objtype="wolves",
                known_cb=badwolf_cb,
                known_cb_key="x",
            )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 5

        stdout = captured.out.splitlines()
        assert not stdout

        assert stderr[0] == "** ERROR: Valid wolves:"
        assert stderr[1] == "  a"
        assert stderr[2] == "  b"
        assert stderr[3] == ""
        assert stderr[4] == "** ERROR: No wolves found when searching by badwolf: d, e"

    def test_not_empty(self, capsys):
        """Pass."""
        ctx = cli.context.Context()

        cli.context.check_empty(
            ctx=ctx,
            this_data=[{"a": "1"}],
            prev_data=[{"a": "1", "b": "2"}],
            value_type="badwolf",
            value=["a"],
            objtype="wolves",
            known_cb=badwolf_cb,
            known_cb_key="x",
        )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 1

        stdout = captured.out.splitlines()
        assert not stdout

        assert stderr[0] == "** Found 1 wolves by badwolf: a"


class TestCliJsonFromStream(object):
    """Pass."""

    def test_stdin_empty(self, monkeypatch, capsys):
        """Pass."""
        ctx = cli.context.Context()
        stream = tools.six.StringIO()
        stream.name = "<stdin>"
        monkeypatch.setattr(stream, "isatty", lambda: True)
        with pytest.raises(SystemExit):
            cli.context.json_from_stream(ctx=ctx, stream=stream, src="--badwolf")

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 1

        stdout = captured.out.splitlines()
        assert not stdout

        exp0 = "** ERROR: No input provided on <stdin> for --badwolf"
        assert stderr[0] == exp0

    def test_file_empty(self, monkeypatch, capsys):
        """Pass."""
        ctx = cli.context.Context()
        stream = tools.six.StringIO()
        stream.name = "/bad/wolf"
        monkeypatch.setattr(stream, "isatty", lambda: False)
        content = ""
        stream.write(content)
        stream.seek(0)
        with pytest.raises(SystemExit):
            cli.context.json_from_stream(ctx=ctx, stream=stream, src="--badwolf")

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 2

        stdout = captured.out.splitlines()
        assert not stdout

        exp0 = "** Read {} bytes from /bad/wolf for --badwolf".format(len(content))
        exp1 = "** ERROR: Empty content supplied in /bad/wolf for --badwolf"
        assert stderr[0] == exp0
        assert stderr[1] == exp1

    def test_json_error(self, monkeypatch, capsys):
        """Pass."""
        ctx = cli.context.Context()
        stream = tools.six.StringIO()
        stream.name = "/bad/wolf"
        monkeypatch.setattr(stream, "isatty", lambda: False)
        content = "{{{}}}}"
        stream.write(content)
        stream.seek(0)
        with pytest.raises(SystemExit):
            cli.context.json_from_stream(ctx=ctx, stream=stream, src="--badwolf")

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 3

        stdout = captured.out.splitlines()
        assert not stdout

        exp0 = "** Read {} bytes from /bad/wolf for --badwolf".format(len(content))
        exp1 = "** ERROR: WRAPPED EXCEPTION: json.decoder.JSONDecodeError"
        exp2 = "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)"  # noqa
        assert stderr[0] == exp0
        assert stderr[1] == exp1
        assert stderr[2] == exp2

    def test_json_success(self, monkeypatch, capsys):
        """Pass."""
        ctx = cli.context.Context()
        stream = tools.six.StringIO()
        stream.name = "/bad/wolf"
        monkeypatch.setattr(stream, "isatty", lambda: False)
        content = '[{"x": "v"}]'
        stream.write(content)
        stream.seek(0)
        cli.context.json_from_stream(ctx=ctx, stream=stream, src="--badwolf")

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 2

        stdout = captured.out.splitlines()
        assert not stdout

        exp0 = "** Read {} bytes from /bad/wolf for --badwolf".format(len(content))
        assert stderr[0] == exp0
        assert stderr[1].startswith("** Loaded JSON content from")


class TestCliDictwriter(object):
    """Pass."""

    def test_default(self):
        """Pass."""
        rows = [{"x": "1"}]
        data = cli.context.dictwriter(rows=rows)
        assert data in ['"x"\r\n"1"\r\n', '"x"\n"1"\n']


class TestCliWriteHistFile(object):
    """Pass."""

    def test_default(self, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            histfile = histpath / cli.context.HISTFILE
            monkeypatch.setattr(cli.context, "HISTPATH", format(histpath))
            cli.context.write_hist_file()
            assert histfile.is_file(), list(histpath.iterdir())


class TestCliExcWrap(object):
    """Pass."""

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


class TestCliSpawnShell(object):
    """Pass."""

    def test_default(self, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        monkeypatch.setattr("sys.stdin", tools.six.StringIO("exit()"))

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            monkeypatch.setattr(cli.context, "HISTPATH", format(histpath))

            with pytest.raises(SystemExit):
                cli.context.spawn_shell()


class TestCliRegisterReadline(object):
    """Pass."""

    def test_default(self, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            histfile = histpath / cli.context.HISTFILE
            monkeypatch.setattr(cli.context, "HISTPATH", format(histpath))

            cli.context.register_readline()
            assert histfile.is_file(), list(histpath.iterdir())

    def test_exc(self, monkeypatch, capsys):
        """Pass."""
        monkeypatch.setattr(cli.context, "readline", utils.MockError)
        runner = CliRunner(mix_stderr=False)

        with runner.isolated_filesystem():
            histpath = tools.pathlib.Path(os.getcwd())
            histfile = histpath / cli.context.HISTFILE
            monkeypatch.setattr(cli.context, "HISTPATH", format(histpath))

            cli.context.register_readline()

            assert histfile.is_file(), list(histpath.iterdir())

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
        assert obj.obj is None
        client = obj.start_client(url=url, key=key, secret=secret)
        assert isinstance(client, connect.Connect)
        assert client == obj.obj

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
