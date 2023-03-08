# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pathlib

from ....cli import cli
from ...tests_api.tests_openapi.test_openapi import validate_openapi_spec
from ...utils import load_clirunner


class TestGrpOpenAPIGetSpec:
    def test_get_spec(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        with runner.isolated_filesystem():
            file_name = "axonius_oas_test.yaml"
            file_path = pathlib.Path(file_name)
            args1 = ["openapi", "get-spec", "--export-file", file_name]
            result1 = runner.invoke(cli=cli, args=args1)

            stderr1 = result1.stderr
            exit_code1 = result1.exit_code

            assert not result1.stdout
            assert file_name in stderr1
            assert exit_code1 == 0

            data = file_path.read_text()
            validate_openapi_spec(data=data)

    def test_get_spec_stdout(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args1 = ["openapi", "get-spec", "--export-file", ""]
            result1 = runner.invoke(cli=cli, args=args1)

            stderr1 = result1.stderr
            exit_code1 = result1.exit_code

            assert result1.stdout
            assert stderr1
            assert exit_code1 == 0
