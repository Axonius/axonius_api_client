# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ....tools import json_load
from ...utils import get_cnx_existing, load_clirunner


class TestGrpCnxCmdGetById:
    def test_json_full(self, api_adapters, request, monkeypatch):
        cnx = get_cnx_existing(apiobj=api_adapters)

        runner = load_clirunner(request, monkeypatch)

        args1 = [
            "adapters",
            "cnx",
            "get-by-id",
            "--node-name",
            cnx["node_name"],
            "--name",
            cnx["adapter_name"],
            "--id",
            cnx["id"],
            "--export-format",
            "json-full",
        ]
        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = json_load(stdout1)
        assert isinstance(json1, dict)

    def test_json_config(self, api_adapters, request, monkeypatch):
        cnx = get_cnx_existing(apiobj=api_adapters)

        runner = load_clirunner(request, monkeypatch)

        args1 = [
            "adapters",
            "cnx",
            "get-by-id",
            "--node-name",
            cnx["node_name"],
            "--name",
            cnx["adapter_name"],
            "--id",
            cnx["id"],
            "--export-format",
            "json-config",
        ]
        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = json_load(stdout1)
        assert isinstance(json1, dict)

    def test_json_basic(self, api_adapters, request, monkeypatch):
        cnx = get_cnx_existing(apiobj=api_adapters)

        runner = load_clirunner(request, monkeypatch)

        args1 = [
            "adapters",
            "cnx",
            "get-by-id",
            "--node-name",
            cnx["node_name"],
            "--name",
            cnx["adapter_name"],
            "--id",
            cnx["id"],
            "--export-format",
            "json",
        ]
        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = json_load(stdout1)
        assert isinstance(json1, dict)

    def test_table_schemas(self, api_adapters, request, monkeypatch):
        cnx = get_cnx_existing(apiobj=api_adapters)

        runner = load_clirunner(request, monkeypatch)

        args1 = [
            "adapters",
            "cnx",
            "get-by-id",
            "--node-name",
            cnx["node_name"],
            "--name",
            cnx["adapter_name"],
            "--id",
            cnx["id"],
            "--export-format",
            "table-schemas",
        ]

        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

    def test_table(self, api_adapters, request, monkeypatch):
        cnx = get_cnx_existing(apiobj=api_adapters)

        runner = load_clirunner(request, monkeypatch)

        args1 = [
            "adapters",
            "cnx",
            "get-by-id",
            "--node-name",
            cnx["node_name"],
            "--name",
            cnx["adapter_name"],
            "--id",
            cnx["id"],
            "--export-format",
            "table",
        ]

        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

    def test_str(self, api_adapters, request, monkeypatch):
        cnx = get_cnx_existing(apiobj=api_adapters)

        runner = load_clirunner(request, monkeypatch)

        args1 = [
            "adapters",
            "cnx",
            "get-by-id",
            "--node-name",
            cnx["node_name"],
            "--name",
            cnx["adapter_name"],
            "--id",
            cnx["id"],
            "--export-format",
            "str",
        ]

        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

    def test_str_args(self, api_adapters, request, monkeypatch):
        cnx = get_cnx_existing(apiobj=api_adapters)

        runner = load_clirunner(request, monkeypatch)

        args1 = [
            "adapters",
            "cnx",
            "get-by-id",
            "--node-name",
            cnx["node_name"],
            "--name",
            cnx["adapter_name"],
            "--id",
            cnx["id"],
            "--export-format",
            "str-args",
        ]
        result1 = runner.invoke(cli=cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0
