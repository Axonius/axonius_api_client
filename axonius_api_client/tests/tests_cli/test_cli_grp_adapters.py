# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

from axonius_api_client import cli, tools

from .. import utils


class TestCmdGet(object):
    """Pass."""

    def test_json(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get", "--export-format", "json"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

    def test_csv(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get", "--export-format", "csv"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        csv_cols1 = [
            "name",
            "node_name",
            "node_id",
            "status_raw",
            "cnx_count",
            "cnx_count_ok",
            "cnx_count_bad",
        ]
        utils.check_csv_cols(stdout1, csv_cols1)

    def test_csv_settings(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [
            "-nw",
            "adapters",
            "get",
            "--include-settings",
            "--export-format",
            "csv",
        ]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        csv_cols1 = [
            "name",
            "node_name",
            "node_id",
            "status_raw",
            "cnx_count",
            "cnx_count_ok",
            "cnx_count_bad",
            "adapter_settings",
            "advanced_settings",
        ]
        utils.check_csv_cols(stdout1, csv_cols1)

    def test_find_fail(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get", "--name", "badwolf", "--export-format", "json"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert not stdout1
        assert stderr1
        assert exit_code1 != 0

        errlines1 = stderr1.splitlines()

        assert errlines1[-1].startswith("** ERROR: No adapters found when searching by")
