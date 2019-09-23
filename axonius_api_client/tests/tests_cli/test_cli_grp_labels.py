# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from axonius_api_client import cli, tools

from .. import utils


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCmdGet(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "labels", "get"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

    def test_csv(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "labels", "get", "--export-format", "csv"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert not stdout1
        assert stderr1
        assert exit_code1 != 0


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCmdAddRemove(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "get", "--query", "(adapters > size(0))", "--max-rows", "1"]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        args2 = [cmd, "labels", "add", "--label", "badwolf1", "--label", "badwolf2"]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=result1.stdout)

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.INT)
        assert json2 == 1

        args3 = [cmd, "labels", "remove", "--label", "badwolf1", "--label", "badwolf2"]
        result3 = runner.invoke(cli=cli.cli, args=args3, input=result1.stdout)

        stderr3 = result3.stderr
        stdout3 = result3.stdout
        exit_code3 = result3.exit_code

        assert stdout3
        assert stderr3
        assert exit_code3 == 0

        json3 = tools.json_load(stdout3)
        assert isinstance(json3, tools.INT)
        assert json3 == 1
