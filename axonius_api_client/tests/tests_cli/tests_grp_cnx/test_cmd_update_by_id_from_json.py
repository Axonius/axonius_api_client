# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import json
import os
import pathlib

from axonius_api_client.cli import cli
from axonius_api_client.cli.grp_adapters.grp_cnx import parsing

from ...meta import CsvData, CsvKeys
from ...tests_api.tests_adapters.test_cnx import TestCnxBase
from ...utils import load_clirunner


class TestGrpCnxCmdUpdateByIdFromJson(TestCnxBase):
    def test_update_success(self, api_adapters, request, monkeypatch, csv_cnx):
        runner = load_clirunner(request, monkeypatch)

        with runner.isolated_filesystem():
            config = {CsvKeys.file_path: f"{parsing.SchemaFile.CONTENT}{CsvData.file_contents}"}
            config_dir = pathlib.Path(os.getcwd())
            config_path = config_dir / "config.json"
            config_path.write_text(json.dumps(config))

            args = [
                "adapters",
                "cnx",
                "update-by-id-from-json",
                "--name",
                "csv",
                "--id",
                csv_cnx.client_id,
                "--input-file",
                f"{config_path}",
                "--use-sane-defaults",
                "--no-prompt-previous",
                "--no-prompt-optional",
                "--no-prompt-default",
                "--export-format",
                "json",
            ]

            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            assert "Connection updated with no errors" in result.stderr
