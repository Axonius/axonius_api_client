# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load

from ...utils import get_cnx_existing, load_clirunner


class TestGrpCnxCmdGet:
    @pytest.mark.parametrize("export_format", ["json-full", "json", "json-config"])
    def test_json_exports(self, api_adapters, request, monkeypatch, export_format):
        cnx = get_cnx_existing(apiobj=api_adapters)
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            adapter_name = cnx["adapter_name"]
            uuid = cnx["uuid"]
            schemas = cnx["schemas"]

            args1 = [
                "adapters",
                "cnx",
                "get",
                "--name",
                adapter_name,
                "--export-format",
                export_format,
            ]
            result1 = runner.invoke(cli=cli, args=args1)

            assert result1.stdout
            assert result1.stderr
            assert result1.exit_code == 0
            if export_format == "json-config":
                assert any([x in result1.stdout for x in schemas])
            elif export_format == "json-full":
                assert '"schemas"' in result1.stdout
                assert uuid in result1.stdout
            elif export_format == "json":
                assert '"schemas"' not in result1.stdout
                assert uuid in result1.stdout

            json1 = json_load(result1.stdout)
            assert isinstance(json1, list) and json1
            for item in json1:
                assert isinstance(item, dict)

    @pytest.mark.parametrize("export_format", ["table", "table-schemas", "str", "str-args"])
    def test_str_exports(self, api_adapters, request, monkeypatch, export_format):
        cnx = get_cnx_existing(apiobj=api_adapters)
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            adapter_name = cnx["adapter_name"]
            node_name = cnx["node_name"]
            uuid = cnx["uuid"]
            cid = cnx["id"]
            schemas = cnx["schemas"]

            args1 = [
                "adapters",
                "cnx",
                "get",
                "--name",
                adapter_name,
                "--export-format",
                export_format,
            ]

            result1 = runner.invoke(cli=cli, args=args1)

            assert result1.stdout
            assert result1.stderr
            assert result1.exit_code == 0

            if export_format == "str-args":
                assert (
                    f"--node-name {node_name!r} --name {adapter_name!r} --id {cid!r}\n"
                    in result1.stdout
                )
            elif export_format == "str":
                assert f"{cid}\n" in result1.stdout
            elif export_format == "table-schemas":
                for schema_key in schemas:
                    assert schema_key in result1.stdout
            elif export_format == "table":
                assert cid in result1.stdout
                assert uuid in result1.stdout
