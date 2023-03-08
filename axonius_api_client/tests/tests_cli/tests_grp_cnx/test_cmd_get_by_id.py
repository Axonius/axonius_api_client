# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load

from ...utils import get_cnx_existing, load_clirunner


class TestGrpCnxCmdGetById:
    @pytest.mark.parametrize("export_format", ["json-full", "json", "json-config"])
    def test_json_exports(self, api_adapters, request, monkeypatch, export_format):
        cnx = get_cnx_existing(apiobj=api_adapters)
        adapter_name = cnx["adapter_name"]
        node_name = cnx["node_name"]
        cid = cnx["id"]

        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args1 = [
                "adapters",
                "cnx",
                "get-by-id",
                "--node-name",
                node_name,
                "--name",
                adapter_name,
                "--id",
                cid,
                "--export-format",
                export_format,
            ]
            result1 = runner.invoke(cli=cli, args=args1)

            assert result1.stdout
            assert result1.stderr
            assert result1.exit_code == 0
            json1 = json_load(result1.stdout)
            assert isinstance(json1, dict) and json1

    @pytest.mark.parametrize("export_format", ["table", "table-schemas", "str", "str-args"])
    def test_str_exports(self, api_adapters, request, monkeypatch, export_format):
        cnx = get_cnx_existing(apiobj=api_adapters)
        adapter_name = cnx["adapter_name"]
        node_name = cnx["node_name"]
        cid = cnx["id"]

        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args1 = [
                "adapters",
                "cnx",
                "get-by-id",
                "--node-name",
                node_name,
                "--name",
                adapter_name,
                "--id",
                cid,
                "--export-format",
                export_format,
            ]
            result1 = runner.invoke(cli=cli, args=args1)

            assert result1.stdout
            assert result1.stderr
            assert result1.exit_code == 0
