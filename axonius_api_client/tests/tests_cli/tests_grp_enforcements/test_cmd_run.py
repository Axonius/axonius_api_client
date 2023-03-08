# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load

from ...tests_api.tests_enforcements.test_enforcements import EnforcementsBase
from ...utils import load_clirunner


class TestGrpEnforcementsCmdRun(EnforcementsBase):
    def test_json_export(self, request, monkeypatch, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "run",
                "--value",
                created_set_trigger.name,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert created_set_trigger.name in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, list) and data
            for x in data:
                assert isinstance(x, dict) and x
