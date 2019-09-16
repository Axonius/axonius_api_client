# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
from click.testing import CliRunner

from axonius_api_client import cli


class TestCliHelp(object):
    """Pass."""

    @pytest.mark.parametrize(
        "cmd",
        [
            [],
            ["devices"],
            ["devices", "count"],
            ["devices", "count-by-saved-query"],
            ["devices", "reports"],
            ["devices", "saved-query"],
            ["devices", "saved-query", "get"],
            ["devices", "saved-query", "add"],
            ["devices", "saved-query", "delete"],
            ["devices", "labels"],
            ["devices", "labels", "get"],
            ["devices", "labels", "add"],
            ["devices", "labels", "remove"],
            ["devices", "reports", "missing-adapters"],
            ["devices", "fields"],
            ["devices", "get"],
            ["devices", "get-by-saved-query"],
            ["devices", "get-by-ip"],
            ["devices", "get-by-hostname"],
            ["devices", "get-by-mac"],
            ["devices", "get-by-subnet"],
            ["users"],
            ["users", "count"],
            ["users", "count-by-saved-query"],
            ["users", "reports"],
            ["users", "reports", "missing-adapters"],
            ["users", "saved-query"],
            ["users", "saved-query", "get"],
            ["users", "saved-query", "add"],
            ["users", "saved-query", "delete"],
            ["users", "labels"],
            ["users", "labels", "get"],
            ["users", "labels", "add"],
            ["users", "labels", "remove"],
            ["users", "fields"],
            ["users", "get"],
            ["users", "get-by-saved-query"],
            ["users", "get-by-username"],
            ["users", "get-by-mail"],
            ["adapters"],
            ["adapters", "get"],
            ["adapters", "cnx"],
            ["adapters", "cnx", "get"],
            ["adapters", "cnx", "add"],
            ["adapters", "cnx", "delete"],
            ["adapters", "cnx", "check"],
            ["adapters", "cnx", "discover"],
            ["shell"],
        ],
    )
    def test_cli_help(self, cmd):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        args1 = cmd + ["--help"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        # stderr1 = result1.stderr

        assert stdout1
        # assert stderr1
        assert exit_code1 == 0
