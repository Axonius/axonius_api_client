# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from ...tests_api.tests_openapi.test_openapi import validate_openapi_spec


class TestGrpOpenAPIGetSpec:
    def test_get_spec(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        args1 = ["openapi", "get-spec"]
        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        validate_openapi_spec(data=stdout1)
