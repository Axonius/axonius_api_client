# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click
import pytest
from click.testing import CliRunner

from axonius_api_client import cli


@click.command()
@click.option("-x", type=cli.click_ext.SplitEquals())
def mycli(x):
    """Pass."""
    pass


class TestCliAlias(object):
    """Pass."""

    @pytest.mark.parametrize("cmd", [["devices"], ["users"]])
    def test_ok(self, cmd):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        args1 = cmd + ["--help"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        assert exit_code1 == 0

    @pytest.mark.parametrize("cmd", [["d", "z"], ["u", "z"]])
    def test_fail(self, cmd):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        args1 = cmd + ["--help"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert not stdout1
        assert stderr1
        assert exit_code1 == 2

    @pytest.mark.parametrize("cmd", [["d", "c"], ["u", "c"]])
    def test_toomany(self, cmd):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        args1 = cmd + ["--help"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert not stdout1
        assert stderr1
        assert exit_code1 == 2


class TestCliSplit(object):
    """Pass."""

    def test_ok(self):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        args1 = ["-x", "a=a"]
        result1 = runner.invoke(cli=mycli, args=args1)

        exit_code1 = result1.exit_code
        assert exit_code1 == 0

    def test_fail(self):
        """Pass."""
        runner = CliRunner(mix_stderr=False)

        args1 = ["-x", "a"]
        result1 = runner.invoke(cli=mycli, args=args1)

        exit_code1 = result1.exit_code
        assert exit_code1 == 2
