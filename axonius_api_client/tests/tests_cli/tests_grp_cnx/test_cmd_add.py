# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import os
import pathlib

import pytest

from axonius_api_client.cli import cli

from ...meta import CsvData, CsvKeys
from ...utils import load_clirunner
from .test_cnx_base import CnxBase


class TestGrpCnxCmdAdd(CnxBase):
    @pytest.fixture
    def cmd(self):
        return "add"

    def test_add_remove_prompt(self, api_adapters, request, cmd, monkeypatch):
        """Test that we only get prompted for the required item user_id in csv adapter."""
        runner = load_clirunner(request, monkeypatch)

        with runner.isolated_filesystem():
            file_dir = pathlib.Path(os.getcwd())
            file_path = file_dir / "data.csv"
            file_path.write_text(CsvData.file_contents)

            args = [
                "adapters",
                "cnx",
                cmd,
                "--name",
                "csv",
                "--config",
                f"{CsvKeys.file_path}={file_path}",
                "--use-sane-defaults",
                "--no-prompt-optional",
                "--no-prompt-default",
                "--export-format",
                "json",
            ]
            prompt_input = [f"{CsvData.user_id}"]

            result = runner.invoke(cli=cli, args=args, input="\n".join(prompt_input))

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            assert "Connection added with no errors" in result.stderr

            # get rid of the input lines, shows up in stdout
            prompt_len = len(prompt_input)
            content = "\n".join(result.stdout.splitlines()[prompt_len:])
            self.delete_cnx_from_content(runner=runner, content=content)

    def test_add_remove_no_prompt(self, api_adapters, request, cmd, monkeypatch):
        """Test that we do not get prompted if we provide the appropriate config keys on the CLI."""
        runner = load_clirunner(request, monkeypatch)

        with runner.isolated_filesystem():
            file_dir = pathlib.Path(os.getcwd())
            file_path = file_dir / "data.csv"
            file_path.write_text(CsvData.file_contents)

            args = [
                "adapters",
                "cnx",
                cmd,
                "--name",
                "csv",
                "--config",
                f"{CsvKeys.file_path}={file_path}",
                "--config",
                f"{CsvKeys.user_id}={CsvData.user_id}",
                "--use-sane-defaults",
                "--no-prompt-optional",
                "--no-prompt-default",
                "--export-format",
                "json",
            ]

            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            assert "Connection added with no errors" in result.stderr
            self.delete_cnx_from_content(runner=runner, content=result.stdout)

    def test_add_remove_no_prompt_error(self, api_adapters, request, cmd, monkeypatch):
        """Test that adding a connection that has errors still returns the data

        we do this by not actually supplying a file_id=path to csv connection
        """
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "adapters",
                "cnx",
                cmd,
                "--name",
                "csv",
                "--config",
                f"{CsvKeys.user_id}={CsvData.user_id}",
                "--use-sane-defaults",
                "--no-prompt-optional",
                "--no-prompt-default",
                "--export-format",
                "json",
            ]

            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 100
            assert "Connection added with error:" in result.stderr

            self.delete_cnx_from_content(runner=runner, content=result.stdout)
