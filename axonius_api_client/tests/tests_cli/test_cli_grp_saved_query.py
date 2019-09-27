# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from axonius_api_client import cli, tools

from .. import utils


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCmdAddGetDelete(object):
    """Pass."""

    def test_query_file(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        name = "badwolf"
        field = "labels"
        cfilter = "generic:{}=a".format(field)

        qf_contents = '(adapters == "aws_adapter")'
        qf_file = "qf.txt"

        args1 = [
            cmd,
            "saved-query",
            "add",
            "--name",
            name,
            "--query-file",
            qf_file,
            "--sort-field",
            field,
            "--column-filter",
            cfilter,
        ]

        with runner.isolated_filesystem():
            with open(qf_file, "w") as f:
                f.write(qf_contents)

            result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, dict)
        assert json1["name"] == name

        args2 = [cmd, "saved-query", "get-by-name", "--name", name]

        result2 = runner.invoke(cli=cli.cli, args=args2)

        exit_code2 = result2.exit_code
        stdout2 = result2.stdout
        stderr2 = result2.stderr

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, dict)
        assert json2["name"] == name

        args3 = [cmd, "saved-query", "delete", "--wait", "0", "-n", name]

        result3 = runner.invoke(cli=cli.cli, args=args3)

        exit_code3 = result3.exit_code
        stdout3 = result3.stdout
        stderr3 = result3.stderr
        assert not stdout3.strip()
        assert stderr3
        assert exit_code3 == 0

        assert not result3.stdout

    def test_json_cf(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        name = "badwolf"
        query = "(adapters > size(0))"
        field = "labels"
        cfilter = "generic:{}=a".format(field)

        args1 = [
            cmd,
            "saved-query",
            "add",
            "--name",
            name,
            "--query",
            query,
            "--sort-field",
            field,
            "--column-filter",
            cfilter,
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, dict)
        assert json1["name"] == name

        args2 = [cmd, "saved-query", "get-by-name", "--name", name]

        result2 = runner.invoke(cli=cli.cli, args=args2)

        exit_code2 = result2.exit_code
        stdout2 = result2.stdout
        stderr2 = result2.stderr

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, dict)
        assert json2["name"] == name

        args3 = [cmd, "saved-query", "delete", "--wait", "0", "-n", name]

        result3 = runner.invoke(cli=cli.cli, args=args3)

        exit_code3 = result3.exit_code
        stdout3 = result3.stdout
        stderr3 = result3.stderr
        assert not stdout3.strip()
        assert stderr3
        assert exit_code3 == 0

        assert not result3.stdout

    def test_json_no_cf(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        name = "badwolf"
        query = "(adapters > size(0))"
        field = "labels"

        args1 = [
            cmd,
            "saved-query",
            "add",
            "--name",
            name,
            "--query",
            query,
            "--sort-field",
            field,
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, dict)
        assert json1["name"] == name

        args2 = [cmd, "saved-query", "get-by-name", "--name", name]

        result2 = runner.invoke(cli=cli.cli, args=args2)

        exit_code2 = result2.exit_code
        stdout2 = result2.stdout
        stderr2 = result2.stderr

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, dict)
        assert json2["name"] == name

        args3 = [cmd, "saved-query", "delete", "--wait", "0", "-n", name]

        result3 = runner.invoke(cli=cli.cli, args=args3)

        exit_code3 = result3.exit_code
        stdout3 = result3.stdout
        stderr3 = result3.stderr
        assert not stdout3.strip()
        assert stderr3
        assert exit_code3 == 0

        assert not result3.stdout

    def test_bad_cf(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        name = "badwolf"
        query = "(adapters > size(0))"
        field = "labels"
        cfilter = "generic:{}".format(field)

        args1 = [
            cmd,
            "saved-query",
            "add",
            "--name",
            name,
            "--query",
            query,
            "--sort-field",
            field,
            "--column-filter",
            cfilter,
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = not result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 != 0


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCmdGet(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "saved-query", "get", "--export-format", "json"]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

    def test_csv(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "saved-query", "get", "--max-rows", "1", "--export-format", "csv"]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        csv_cols1 = ["name", "date_fetched", "timestamp"]
        utils.check_csv_cols(stdout1, csv_cols1)
