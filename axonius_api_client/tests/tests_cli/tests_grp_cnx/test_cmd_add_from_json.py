# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import os
import pathlib

import pytest

from axonius_api_client.cli import cli
from axonius_api_client.tools import json_dump

from ...meta import CsvData, CsvKeys
from ...utils import load_clirunner
from .test_cnx_base import CnxBase


class TestGrpCnxCmdAddFromJson(CnxBase):
    @pytest.fixture
    def cmd(self):
        return "add-from-json"

    def test_add_remove_input_stdin(self, api_adapters, request, cmd, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        with runner.isolated_filesystem():
            file_dir = pathlib.Path(os.getcwd())
            file_path = file_dir / "data.csv"
            file_path.write_text(CsvData.file_contents)

            config = {**CsvData.config, CsvKeys.file_path: f"{file_path}"}
            config_str = json_dump(config)

            args = [
                "adapters",
                "cnx",
                cmd,
                "--name",
                "csv",
                "--use-sane-defaults",
                "--export-format",
                "json",
            ]

            result = runner.invoke(cli=cli, args=args, input=config_str)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            assert "Connection added with no errors" in result.stderr

            self.delete_cnx_from_content(runner=runner, content=result.stdout)

    def test_add_remove_input_stdin_error(self, api_adapters, request, cmd, monkeypatch):
        """Test that adding a connection that has errors still returns the data

        we do this by not actually supplying a file_id=path to csv connection
        """
        runner = load_clirunner(request, monkeypatch)

        with runner.isolated_filesystem():
            file_dir = pathlib.Path(os.getcwd())
            file_path = file_dir / "data.csv"
            file_path.write_text(CsvData.file_contents)

            config = {**CsvData.config}
            config_str = json_dump(config)

            args = [
                "adapters",
                "cnx",
                cmd,
                "--name",
                "csv",
                "--use-sane-defaults",
                "--export-format",
                "json",
            ]

            result = runner.invoke(cli=cli, args=args, input=config_str)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 100
            assert "Connection added with error:" in result.stderr

            self.delete_cnx_from_content(runner=runner, content=result.stdout)

    def test_add_remove_input_file(self, api_adapters, request, cmd, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        with runner.isolated_filesystem():
            file_dir = pathlib.Path(os.getcwd())
            file_path = file_dir / "data.csv"
            file_path.write_text(CsvData.file_contents)

            config = {**CsvData.config, CsvKeys.file_path: f"{file_path}"}
            config_str = json_dump(config)
            config_path = file_dir / "data.json"
            config_path.write_text(config_str)

            args = [
                "adapters",
                "cnx",
                cmd,
                "--name",
                "csv",
                "--input-file",
                f"{config_path}",
                "--use-sane-defaults",
                "--export-format",
                "json",
            ]

            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            assert "Connection added with no errors" in result.stderr

            self.delete_cnx_from_content(runner=runner, content=result.stdout)
