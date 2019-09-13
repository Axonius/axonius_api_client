# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import json

from axonius_api_client import cli, tools

from . import utils


class TestCliAdapters(object):
    """Pass."""

    def test_json(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli, args=["adapters", "get", "--export-format", "json"]
        )

        assert result.exit_code == 0

        json_reloaded = json.loads(result.stdout)
        assert isinstance(json_reloaded, tools.LIST)

    def test_csv(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli, args=["adapters", "get", "--export-format", "csv"]
        )
        assert result.exit_code == 0

        utils.check_csv_cols(
            result.stdout,
            [
                "name",
                "node_name",
                "node_id",
                "status_raw",
                "cnx_count",
                "cnx_count_ok",
                "cnx_count_bad",
            ],
        )

    def test_csv_settings(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli,
            args=["adapters", "get", "--include-settings", "--export-format", "csv"],
        )
        assert result.exit_code == 0

        utils.check_csv_cols(
            result.stdout,
            [
                "name",
                "node_name",
                "node_id",
                "status_raw",
                "cnx_count",
                "cnx_count_ok",
                "cnx_count_bad",
                "adapter_settings",
                "advanced_settings",
            ],
        )

    def test_find_fail(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli,
            args=["adapters", "get", "--name", "badwolf", "--export-format", "json"],
        )

        assert result.exit_code != 0

        stderr = result.stderr.splitlines()

        assert stderr[-1].startswith("** ERROR: No adapters found when searching by")
