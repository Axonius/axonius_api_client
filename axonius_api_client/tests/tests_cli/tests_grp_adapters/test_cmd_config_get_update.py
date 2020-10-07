# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ....constants.adapters import CSV_ADAPTER
from ....tools import json_dump, json_load
from ...utils import load_clirunner


class TestGrpAdaptersCmdConfigGetUpdate:
    def test_json_full(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        args1 = [
            "adapters",
            "config-get",
            "--name",
            CSV_ADAPTER,
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

    def test_json_basic(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)

        args1 = [
            "adapters",
            "config-get",
            "--name",
            CSV_ADAPTER,
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

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = json_load(stdout2)
        assert isinstance(json2, dict)
        assert json2[key] == new_value

        json2[key] = old_value

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
        result3 = runner.invoke(cli=cli, args=args3, input=json_dump(json2))

        stderr3 = result3.stderr
        stdout3 = result3.stdout
        exit_code3 = result3.exit_code

        assert stdout3
        assert stderr3
        assert exit_code3 == 0

        json3 = json_load(stdout3)
        assert isinstance(json3, dict)
        assert json3[key] == old_value
