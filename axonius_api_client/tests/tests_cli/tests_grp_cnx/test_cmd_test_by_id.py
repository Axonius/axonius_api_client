# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli
from axonius_api_client.exceptions import CnxAddError
from axonius_api_client.tools import json_load

from ...tests_api.tests_adapters.test_cnx import skip_if_no_adapter
from ...utils import get_cnx_working, load_clirunner
from .test_cnx_base import CnxTools


class TestGrpCnxCmdTestById(CnxTools):
    def test_success(self, api_adapters, request, monkeypatch):
        cnx = get_cnx_working(apiobj=api_adapters, reqkeys=["domain"])
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            adapter_name = cnx["adapter_name"]
            adapter_node = cnx["node_name"]
            cnx_id = cnx["id"]

            result_args = [
                "adapters",
                "cnx",
                "test-by-id",
                "--name",
                adapter_name,
                "--node-name",
                adapter_node,
                "--id",
                cnx_id,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=result_args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert "Connection tested with no errors" in result.stderr
            result_json = json_load(result.stdout)
            assert isinstance(result_json, dict) and result_json

    def test_failure(self, api_adapters, request, monkeypatch):
        skip_if_no_adapter(api_adapters, "tanium")
        try:
            api_adapters.cnx.add(adapter_name="tanium", username="x", password="x", domain="x")
        except CnxAddError as exc:
            cnx = exc.cnx_new

        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            adapter_name = cnx["adapter_name"]
            adapter_node = cnx["node_name"]
            cnx_id = cnx["id"]

            result_args = [
                "adapters",
                "cnx",
                "test-by-id",
                "--name",
                adapter_name,
                "--node-name",
                adapter_node,
                "--id",
                cnx_id,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=result_args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 100
            assert "Connection tested with error" in result.stderr
            self.delete_cnx_from_content(runner=runner, content=result.stdout)
