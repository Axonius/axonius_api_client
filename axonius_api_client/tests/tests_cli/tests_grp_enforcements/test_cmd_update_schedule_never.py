# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli

from ...tests_api.tests_enforcements.test_enforcements import EnforcementsBase
from ...utils import load_clirunner


class TestGrpEnforcementsCmdUpdateScheduleNever(EnforcementsBase):
    def test_success(self, request, monkeypatch, apiobj, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-schedule-never",
                "--value",
                created_set_trigger.name,
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            assert created_set_trigger.name in result.stdout
            assert "EnforcementSchedule: None" in result.stdout
            assert "EnforcementSchedule Type: never" in result.stdout
