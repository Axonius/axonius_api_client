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
            ["devices", "missing-adapters"],
            ["devices", "fields"],
            ["devices", "get"],
            ["users"],
            ["users", "missing-adapters"],
            ["users", "fields"],
            ["users", "get"],
            ["adapters"],
            ["adapters", "get"],
            ["adapters", "cnx"],
            ["adapters", "cnx", "get"],
            ["shell"],
        ],
    )
    def test_cli_help(self, cmd):
        """Pass."""
        runner = CliRunner()

        result = runner.invoke(cli=cli.cli, args=cmd + ["--help"])
        assert result.exit_code == 0, cmd
