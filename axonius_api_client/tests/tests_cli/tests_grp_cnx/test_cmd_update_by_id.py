# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import os
import pathlib

from axonius_api_client.cli import cli

from ...meta import CsvData, CsvKeys
from ...tests_api.tests_adapters.test_cnx import TestCnxBase
from ...utils import load_clirunner


class TestGrpCnxCmdUpdateById(TestCnxBase):
    def test_update_success(self, api_adapters, request, monkeypatch, csv_cnx):
        runner = load_clirunner(request, monkeypatch)

        with runner.isolated_filesystem():
            file_dir = pathlib.Path(os.getcwd())
            file_path = file_dir / "data.csv"
            file_path.write_text(CsvData.file_contents)

            args = [
                "adapters",
                "cnx",
                "update-by-id",
                "--name",
                "csv",
                "--id",
                csv_cnx.client_id,
                "--config",
                f"{CsvKeys.file_path}={file_path}",
                "--use-sane-defaults",
                "--no-prompt-previous",
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

            assert "Connection updated with no errors" in result.stderr
