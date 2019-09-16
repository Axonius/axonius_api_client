# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from axonius_api_client import cli, tools

from .. import utils


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCmdMissingAdapters(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [
            cmd,
            "get",
            "--query",
            "(adapters > size(0))",
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        args2 = [
            cmd,
            "reports",
            "missing-adapters",
            "--rows",
            "-",
            "--export-format",
            "json",
        ]

        result2 = runner.invoke(cli=cli.cli, args=args2, input=result1.stdout)

        exit_code2 = result2.exit_code
        stdout2 = result2.stdout
        stderr2 = result2.stderr

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.LIST)

    def test_csv(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [
            cmd,
            "get",
            "--query",
            "(adapters > size(0))",
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        args2 = [
            cmd,
            "reports",
            "missing-adapters",
            "--rows",
            "-",
            "--export-format",
            "csv",
        ]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=result1.stdout)

        exit_code2 = result2.exit_code
        stdout2 = result2.stdout
        stderr2 = result2.stderr

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        csv_cols2 = ["missing", "missing_nocnx", "adapters"]
        utils.check_csv_cols(stdout2, csv_cols2)
