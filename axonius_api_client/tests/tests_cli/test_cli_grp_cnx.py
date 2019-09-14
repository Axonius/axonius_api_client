# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

from axonius_api_client import cli, tools

from .. import utils


class TestCliGrpCnxCmdGet(object):
    """Pass."""

    def test_json(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result1 = runner.invoke(cli=cli.cli, args=["adapters", "get"])

        assert result1.exit_code == 0

        result2 = runner.invoke(
            cli=cli.cli,
            args=[
                "adapters",
                "cnx",
                "get",
                "--adapters",
                "-",
                "--export-format",
                "json",
            ],
            input=result1.stdout,
        )

        assert result2.exit_code == 0

        json_stdout = tools.json_load(result2.stdout)
        assert isinstance(json_stdout, tools.LIST)

    def test_csv(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result1 = runner.invoke(cli=cli.cli, args=["adapters", "get"])

        assert result1.exit_code == 0

        result2 = runner.invoke(
            cli=cli.cli,
            args=[
                "adapters",
                "cnx",
                "get",
                "--adapters",
                "-",
                "--export-format",
                "csv",
            ],
            input=result1.stdout,
        )

        assert result2.exit_code == 0

        utils.check_csv_cols(
            result2.stdout,
            ["adapter_name", "node_name", "id", "uuid", "status_raw", "error"],
        )

    def test_csv_settings(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result1 = runner.invoke(cli=cli.cli, args=["adapters", "get"])

        assert result1.exit_code == 0

        result2 = runner.invoke(
            cli=cli.cli,
            args=[
                "adapters",
                "cnx",
                "get",
                "--adapters",
                "-",
                "--export-format",
                "csv",
                "--include-settings",
            ],
            input=result1.stdout,
        )

        assert result2.exit_code == 0

        utils.check_csv_cols(
            result2.stdout,
            [
                "adapter_name",
                "node_name",
                "id",
                "uuid",
                "status_raw",
                "error",
                "settings",
            ],
        )

    def test_non_adapters_json(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        content = [{"x": "a"}]

        result = runner.invoke(
            cli=cli.cli,
            args=["adapters", "cnx", "get", "--adapters", "-"],
            input=tools.json_dump(content),
        )

        assert result.exit_code != 0

        stderr = result.stderr.splitlines()

        exp = "** ERROR: No 'cnx' key found in adapter with keys: {}".format(
            list(content[0])
        )
        assert stderr[-1] == exp
