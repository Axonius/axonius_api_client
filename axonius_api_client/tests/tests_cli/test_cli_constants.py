# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import os

from click.testing import CliRunner

from axonius_api_client import cli


class TestCliLoadEnv(object):
    """Pass."""

    def test_axenv(self, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            with open("test.env", "w") as f:
                f.write("AX_TEST=badwolf1\n")
            monkeypatch.delenv("AX_TEST", raising=False)
            monkeypatch.setenv("AX_ENV", "test.env")
            cli.cli_constants.load_dotenv(reenv=True)
            assert os.environ["AX_TEST"] == "badwolf1"

    def test_default(self, monkeypatch):
        """Pass."""
        runner = CliRunner(mix_stderr=False)
        with runner.isolated_filesystem():
            with open(".env", "w") as f:
                f.write("AX_TEST=badwolf2\n")
            monkeypatch.delenv("AX_TEST", raising=False)
            monkeypatch.delenv("AX_ENV", raising=False)
            cli.cli_constants.load_dotenv(reenv=True)
            assert os.environ["AX_TEST"] == "badwolf2"
