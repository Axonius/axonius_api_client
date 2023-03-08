# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from axonius_api_client.cli import cli

from ...tests_api.tests_adapters.test_cnx import skip_if_no_adapter
from ...utils import get_cnx_working, load_clirunner
from .test_cnx_base import CnxBase


class TestGrpCnxCmdTestDirect(CnxBase):
    @pytest.fixture
    def cmd(self):
        return "test"

    def test_success(self, api_adapters, request, monkeypatch):
        cnx = get_cnx_working(apiobj=api_adapters, reqkeys=["domain"])
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            adapter_name = cnx["adapter_name"]
            adapter_node = cnx["node_name"]
            config = cnx["config"]
            result_args = [
                "adapters",
                "cnx",
                "test",
                "--name",
                adapter_name,
                "--node-name",
                adapter_node,
            ]
            for k, v in config.items():
                result_args += ["--config", f"{k}={v}"]

            result = runner.invoke(cli=cli, args=result_args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert "Connection tested with no errors" in result.stderr

    def test_failure(self, api_adapters, request, monkeypatch):
        skip_if_no_adapter(api_adapters, "tanium")
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            adapter_name = "tanium"
            config = {
                "username": "x",
                "password": "x",
                "domain": "x",
            }
            result_args = [
                "adapters",
                "cnx",
                "test",
                "--name",
                adapter_name,
                "--no-prompt-default",
                "--no-prompt-optional",
            ]
            for k, v in config.items():
                result_args += ["--config", f"{k}={v}"]

            result = runner.invoke(cli=cli, args=result_args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 100
            assert "Connection tested with error" in result.stderr
