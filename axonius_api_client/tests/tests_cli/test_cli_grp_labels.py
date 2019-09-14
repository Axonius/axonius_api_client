# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from axonius_api_client import cli, tools

from .. import utils


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCliGrpLabelsCmdGet(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result2 = runner.invoke(
            cli=cli.cli, args=[cmd, "labels", "get", "--export-format", "json"]
        )

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert exit_code2 == 0, stderr2

        json_stdout = tools.json_load(stdout2)
        assert isinstance(json_stdout, tools.LIST)

    def test_csv(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result2 = runner.invoke(
            cli=cli.cli, args=[cmd, "labels", "get", "--export-format", "csv"]
        )

        stderr2 = result2.stderr
        exit_code2 = result2.exit_code

        assert exit_code2 != 0, stderr2


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCliGrpLabelsCmdAddRemove(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args = [
            cmd,
            "get",
            "--query",
            "(adapters > size(0))",
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        result1 = runner.invoke(cli=cli.cli, args=args)

        assert result1.exit_code == 0

        result2 = runner.invoke(
            cli=cli.cli,
            args=[
                cmd,
                "labels",
                "add",
                "--label",
                "badwolf1",
                "--label",
                "badwolf2",
                "--export-format",
                "json",
            ],
            input=result1.stdout,
        )

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert exit_code2 == 0, stderr2

        json_stdout = tools.json_load(stdout2)
        assert isinstance(json_stdout, tools.INT)
        assert json_stdout == 1

        result2 = runner.invoke(
            cli=cli.cli,
            args=[
                cmd,
                "labels",
                "remove",
                "--label",
                "badwolf1",
                "--label",
                "badwolf2",
                "--export-format",
                "json",
            ],
            input=result1.stdout,
        )

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert exit_code2 == 0, stderr2

        json_stdout = tools.json_load(stdout2)
        assert isinstance(json_stdout, tools.INT)
        assert json_stdout == 1
