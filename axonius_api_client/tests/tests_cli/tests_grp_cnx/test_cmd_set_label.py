# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load

from ...utils import get_cnx_existing, load_clirunner
from .test_cnx_base import CnxTools


class TestGrpCnxCmdSetLabel(CnxTools):
    def test_set_revert(self, api_adapters, request, monkeypatch):
        cnx = get_cnx_existing(apiobj=api_adapters)
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            value_orig = cnx["connection_label"]
            value_update = "bananarama"

            adapter_name = cnx["adapter_name"]
            adapter_node = cnx["node_name"]
            cnx_id = cnx["id"]

            update_args = [
                "adapters",
                "cnx",
                "set-label",
                "--name",
                adapter_name,
                "--node-name",
                adapter_node,
                "--id",
                cnx_id,
                "--label",
                value_update,
                "--export-format",
                "json",
            ]
            update = runner.invoke(cli=cli, args=update_args)

            assert update.stdout
            assert update.stderr
            assert update.exit_code == 0
            assert "Connection updated with no errors" in update.stderr

            update_json = json_load(update.stdout)
            assert isinstance(update_json, dict) and update_json

            revert_args = [
                "adapters",
                "cnx",
                "set-label",
                "--name",
                adapter_name,
                "--node-name",
                adapter_node,
                "--id",
                f"{cnx_id}",
                "--label",
                value_orig,
                "--export-format",
                "json",
            ]
            revert = runner.invoke(cli=cli, args=revert_args)

            assert revert.stdout
            assert revert.stderr
            assert revert.exit_code == 0
            assert "Connection updated with no errors" in revert.stderr
            revert_json = json_load(revert.stdout)
            assert isinstance(revert_json, dict) and revert_json
