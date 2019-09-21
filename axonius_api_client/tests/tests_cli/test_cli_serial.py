# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from axonius_api_client import cli, tools

from .. import utils


def badwolf_cb(x, **kwargs):
    """Pass."""
    return ["a", "b"]


def to_json(ctx, raw_data, **kwargs):
    """Pass."""
    return tools.json_dump(obj=raw_data, **kwargs)


class TestCliJoins(object):
    """Pass."""

    def test_kv(self):
        """Pass."""
        x = cli.serial.join_kv({"a": "b", "c": "d"})
        assert x == "\n  a: b\n  c: d"

    def test_tv(self):
        """Pass."""
        x = cli.serial.join_tv(
            {"a": {"title": "a", "value": 1}, "b": {"title": "b", "value": 2}}
        )
        assert x == "a: 1\nb: 2"

    def test_cr(self):
        """Pass."""
        x = cli.serial.join_cr(["a", "b"])
        assert x == "a\nb"

    def test_cr_maxlen(self):
        """Pass."""
        obj = ["a" * (cli.cli_constants.MAX_LEN + 1000)]
        x = cli.serial.join_cr(obj=obj, is_cell=True)
        assert "TRIMMED" in x.splitlines()[-1]


class TestCliToJson(object):
    """Pass."""

    def test_default(self):
        """Pass."""
        x = cli.serial.to_json(ctx=None, raw_data=[])
        assert x == "[]"


class TestCliJsonToRows(object):
    """Pass."""

    def test_stdin_empty(self, monkeypatch, capsys):
        """Pass."""
        ctx = utils.get_mockctx()

        stream = tools.six.StringIO()
        stream.name = "<stdin>"
        monkeypatch.setattr(stream, "isatty", lambda: True)

        this_cmd = "bad wolf check --rows"
        src_cmds = ["bad wolf get"]

        with pytest.raises(SystemExit):
            cli.serial.json_to_rows(
                ctx=ctx, stream=stream, this_cmd=this_cmd, src_cmds=src_cmds
            )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert stderr

        stdout = captured.out.splitlines()
        assert not stdout

        exp = "** ERROR: No input provided on {!r} for {!r}"
        exp = exp.format(stream.name, this_cmd)
        assert stderr[-1] == exp

    def test_file_empty(self, monkeypatch, capsys):
        """Pass."""
        ctx = utils.get_mockctx()

        stream = tools.six.StringIO()
        stream.name = "/bad/wolf"
        monkeypatch.setattr(stream, "isatty", lambda: False)

        content = ""
        stream.write(content)
        stream.seek(0)

        this_cmd = "bad wolf check --rows"
        src_cmds = ["bad wolf get"]

        with pytest.raises(SystemExit):
            cli.serial.json_to_rows(
                ctx=ctx, stream=stream, this_cmd=this_cmd, src_cmds=src_cmds
            )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert stderr

        stdout = captured.out.splitlines()
        assert not stdout

        exp = "** ERROR: Empty content supplied in {!r} for {!r}"
        exp = exp.format(stream.name, this_cmd)
        assert stderr[-1] == exp

    def test_json_error(self, monkeypatch, capsys):
        """Pass."""
        ctx = utils.get_mockctx()

        stream = tools.six.StringIO()
        stream.name = "/bad/wolf"
        monkeypatch.setattr(stream, "isatty", lambda: False)

        content = "{{{}}}}"
        stream.write(content)
        stream.seek(0)

        this_cmd = "bad wolf check --rows"
        src_cmds = ["bad wolf get"]

        with pytest.raises(SystemExit):
            cli.serial.json_to_rows(
                ctx=ctx, stream=stream, this_cmd=this_cmd, src_cmds=src_cmds
            )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert stderr

        stdout = captured.out.splitlines()
        assert not stdout

        exp0 = "** Read {} bytes from {!r} for {!r}"
        exp0 = exp0.format(len(content), stream.name, this_cmd)
        exp1 = "** ERROR: WRAPPED EXCEPTION: json.decoder.JSONDecodeError"
        exp2 = "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)"  # noqa
        assert stderr[0] == exp0
        assert stderr[1] == exp1
        assert stderr[2] == exp2

    def test_json_success(self, monkeypatch, capsys):
        """Pass."""
        ctx = utils.get_mockctx()

        stream = tools.six.StringIO()
        stream.name = "/bad/wolf"
        monkeypatch.setattr(stream, "isatty", lambda: False)

        content = '[{"x": "v"}]'
        stream.write(content)
        stream.seek(0)

        this_cmd = "bad wolf check --rows"
        src_cmds = ["bad wolf get"]

        cli.serial.json_to_rows(
            ctx=ctx, stream=stream, this_cmd=this_cmd, src_cmds=src_cmds
        )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 2

        stdout = captured.out.splitlines()
        assert not stdout

        exp0 = "** Read {} bytes from {!r} for {!r}"
        exp0 = exp0.format(len(content), stream.name, this_cmd)
        exp1 = "** Loaded JSON rows as list"
        assert stderr[0] == exp0
        assert stderr[1].startswith(exp1)


class TestCliDictwriter(object):
    """Pass."""

    def test_default(self):
        """Pass."""
        rows = [{"x": "1"}]
        data = cli.serial.dictwriter(rows=rows)
        assert data in ['"x"\r\n"1"\r\n', '"x"\n"1"\n']


class TestCliCollapseRows(object):
    """Pass."""

    def test_default(self):
        """Pass."""
        rows = [{"cnx": [{"id": "1"}]}, {"id": "2"}, {"cnx": {"id": "3"}}]
        x = cli.serial.collapse_rows(rows=rows, key="cnx")
        exp = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        assert x == exp


class TestCliObjToCsv(object):
    """Pass."""

    def test_default(self):
        """Pass."""
        ctx = utils.get_mockctx()
        rows = [{"cnx": [{"id": "1"}]}, {"id": "2"}, {"cnx": {"id": "3"}}]
        x = cli.serial.obj_to_csv(ctx=ctx, raw_data=rows)
        exp = (
            '"cnx.id","id","cnx"\r\n"1","",""\r\n"","2",""\r\n"","","Data'
            ' of type dict is too complex for CSV format"\r\n'
        )

        assert x == exp


class TestCliEnsureKeys(object):
    """Pass."""

    def test_default(self):
        """Pass."""
        ctx = utils.get_mockctx()
        rows = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        this_cmd = "bad wolf check --rows"
        src_cmds = ["bad wolf get"]
        keys = ["id"]
        cli.serial.ensure_keys(
            ctx=ctx,
            rows=rows,
            src_cmds=src_cmds,
            this_cmd=this_cmd,
            keys=keys,
            all_items=False,
        )

    def test_missing(self, capsys):
        """Pass."""
        ctx = utils.get_mockctx()
        rows = [{"id": "1"}, {"noid": "2"}, {"id": "3"}]
        this_cmd = "bad wolf check --rows"
        src_cmds = ["bad wolf get"]
        keys = ["id"]

        with pytest.raises(SystemExit):
            cli.serial.ensure_keys(
                ctx=ctx,
                rows=rows,
                src_cmds=src_cmds,
                this_cmd=this_cmd,
                keys=keys,
                all_items=True,
            )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert stderr

        stdout = captured.out.splitlines()
        assert not stdout

        exp = "  Item must have keys: {}"
        exp = exp.format(list(keys))
        assert stderr[-2] == exp


class TestCliCheckRowsType(object):
    """Pass."""

    def test_default(self):
        """Pass."""
        ctx = utils.get_mockctx()
        rows = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        this_cmd = "bad wolf check --rows"
        src_cmds = ["bad wolf get"]

        cli.serial.check_rows_type(
            ctx=ctx, rows=rows, src_cmds=src_cmds, this_cmd=this_cmd, all_items=False
        )

    def test_missing(self, capsys):
        """Pass."""
        ctx = utils.get_mockctx()
        rows = [{"id": "1"}, [{"noid": "2"}], {"id": "3"}]
        this_cmd = "bad wolf check --rows"
        src_cmds = ["bad wolf get"]

        with pytest.raises(SystemExit):
            cli.serial.check_rows_type(
                ctx=ctx, rows=rows, src_cmds=src_cmds, this_cmd=this_cmd, all_items=True
            )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert stderr

        stdout = captured.out.splitlines()
        assert not stdout

        exp = "** ERROR: Item #2 in input"
        assert stderr[-1].startswith(exp)
