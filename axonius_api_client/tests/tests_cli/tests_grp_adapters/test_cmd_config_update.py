# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli
from axonius_api_client.constants.adapters import CSV_ADAPTER
from axonius_api_client.tools import json_dump, json_load

from ...utils import load_clirunner


class TestGrpAdaptersCmdConfigUpdate:
    def test_update(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args1 = [
                "adapters",
                "config-get",
                "--name",
                CSV_ADAPTER,
                "--export-format",
                "json",
            ]
            result1 = runner.invoke(cli=cli, args=args1)

            assert result1.stdout
            assert result1.stderr
            assert result1.exit_code == 0

            json1 = json_load(result1.stdout)
            assert isinstance(json1, dict)

            key = "user_last_fetched_threshold_hours"
            old_value = json1.get(key, 48)
            new_value = old_value + 1

            args2 = [
                "adapters",
                "config-update",
                "--name",
                CSV_ADAPTER,
                "--export-format",
                "json",
                "--config",
                f"{key}={new_value}",
            ]
            result2 = runner.invoke(cli=cli, args=args2)

            assert result2.stdout
            assert result2.stderr
            assert result2.exit_code == 0

            json2 = json_load(result2.stdout)
            assert isinstance(json2, dict)
            assert json2[key] == new_value

            revert = {key: old_value}

            args3 = [
                "adapters",
                "config-update-from-json",
                "--name",
                CSV_ADAPTER,
                "--export-format",
                "json",
                "--input-file",
                "-",
            ]
            result3 = runner.invoke(cli=cli, args=args3, input=json_dump(revert))

            assert result3.stderr
            assert result3.stdout
            assert result3.exit_code == 0

            json3 = json_load(result3.stdout)
            assert isinstance(json3, dict)
            assert json3[key] == old_value
