# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from axonius_api_client import cli, tools

from .. import utils


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCliGrpObjectsCmdMissingAdapters(object):
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
                "reports",
                "missing-adapters",
                "--rows",
                "-",
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
        assert isinstance(json_stdout, tools.LIST)

    def test_csv(self, request, monkeypatch, cmd):
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
                "reports",
                "missing-adapters",
                "--rows",
                "-",
                "--export-format",
                "csv",
            ],
            input=result1.stdout,
        )

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert exit_code2 == 0, stderr2

        utils.check_csv_cols(stdout2, ["missing", "missing_nocnx", "adapters"])
