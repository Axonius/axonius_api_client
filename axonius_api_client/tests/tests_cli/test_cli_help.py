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
            ["adapters", "cnx", "add"],
            ["adapters", "cnx", "check"],
            ["adapters", "cnx", "delete"],
            ["adapters", "cnx", "discover"],
            ["adapters", "cnx", "get"],
            ["adapters", "cnx"],
            ["adapters", "get"],
            ["adapters"],
            ["d"],
            ["devices", "count"],
            ["devices", "count-by-saved-query"],
            ["devices", "fields"],
            ["devices", "get"],
            ["devices", "get-by-hostname"],
            ["devices", "get-by-ip"],
            ["devices", "get-by-mac"],
            ["devices", "get-by-saved-query"],
            ["devices", "get-by-subnet"],
            ["devices", "labels", "add"],
            ["devices", "labels", "get"],
            ["devices", "labels", "remove"],
            ["devices", "labels"],
            ["devices", "reports", "missing-adapters"],
            ["devices", "reports"],
            ["devices", "saved-query", "add"],
            ["devices", "saved-query", "delete"],
            ["devices", "saved-query", "get"],
            ["devices", "saved-query", "get-by-name"],
            ["devices", "saved-query"],
            ["devices"],
            ["tools", "write-config"],
            ["tools", "shell"],
            ["tools"],
            ["u"],
            ["users", "count"],
            ["users", "count-by-saved-query"],
            ["users", "fields"],
            ["users", "get"],
            ["users", "get-by-mail"],
            ["users", "get-by-saved-query"],
            ["users", "get-by-username"],
            ["users", "labels", "add"],
            ["users", "labels", "get"],
            ["users", "labels", "remove"],
            ["users", "labels"],
            ["users", "reports", "missing-adapters"],
            ["users", "reports"],
            ["users", "saved-query", "add"],
            ["users", "saved-query", "delete"],
            ["users", "saved-query", "get"],
            ["users", "saved-query", "get-by-name"],
            ["users", "saved-query"],
            ["users"],
            [],
        ],
    )
    def test_help(self, cmd):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        args1 = cmd + ["--help"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout

        assert stdout1
        assert exit_code1 == 0

    @pytest.mark.parametrize(
        "cmd",
        [
            ["adapters", "cnx", "check"],
            ["adapters", "cnx", "delete"],
            ["adapters", "cnx", "discover"],
            ["adapters", "cnx", "get"],
            ["devices", "labels", "add"],
            ["devices", "labels", "remove"],
            ["devices", "reports", "missing-adapters"],
            ["users", "labels", "add"],
            ["users", "labels", "remove"],
            ["users", "reports", "missing-adapters"],
        ],
    )
    def test_show_sources(self, cmd):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        args1 = cmd + ["-ss"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert not stdout1
        assert stderr1
        assert exit_code1 == 0
