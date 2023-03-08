# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""

from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load, listify

from ...utils import load_clirunner


class CnxTools:
    def delete_cnx_from_content(self, runner, content):
        data = json_load(content)
        assert isinstance(data, (list, dict)) and data

        for cnx in listify(data):
            with runner.isolated_filesystem():
                cnx_id = cnx["id"]
                adapter_name = cnx["adapter_name"]
                node_name = cnx["node_name"]
                args = [
                    "adapters",
                    "cnx",
                    "delete-by-id",
                    "--name",
                    adapter_name,
                    "--node-name",
                    node_name,
                    "--id",
                    cnx_id,
                ]

                result = runner.invoke(cli=cli, args=args)

                assert result.stdout
                assert result.stderr
                assert result.exit_code == 0

                exp = f"ID: {cnx_id}"
                assert exp in result.stdout

                assert "Connection deleted!" in result.stderr
                exp = f"CnxDelete(client_id={cnx_id!r}"
                assert exp in result.stderr


class CnxBase(CnxTools):
    def test_show_schemas(self, api_adapters, request, cmd, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = ["adapters", "cnx", cmd, "--name", "csv", "--show-schemas"]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert "Required schemas: " in result.stdout

    def test_show_defaults(self, api_adapters, request, cmd, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = ["adapters", "cnx", cmd, "--name", "csv", "--show-defaults"]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert "schema_defaults: " in result.stdout
