# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli

from ...tests_api.tests_enforcements.test_enforcements import EnforcementsBase
from ...utils import load_clirunner


class TestGrpEnforcementsCmdUpdateScheduleHourly(EnforcementsBase):
    def test_success(self, request, monkeypatch, apiobj, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-schedule-hourly",
                "--value",
                created_set_trigger.name,
                "--recurrence",
                "3",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            assert created_set_trigger.name in result.stdout
            assert "EnforcementSchedule Type: hourly" in result.stdout
            assert "EnforcementSchedule: Every 3 hours" in result.stdout

    def test_invalid_recurrence_bad_day_number_too_low(
        self, request, monkeypatch, apiobj, created_set_trigger
    ):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-schedule-hourly",
                "--value",
                created_set_trigger.name,
                "--recurrence",
                "0",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code != 0

            assert "Supplied value '0' is less than min value of 1." in result.stderr

    def test_invalid_recurrence_bad_day_number_too_high(
        self, request, monkeypatch, apiobj, created_set_trigger
    ):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-schedule-hourly",
                "--value",
                created_set_trigger.name,
                "--recurrence",
                "25",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code != 0

            assert "Supplied value '25' is greater than max value of 24." in result.stderr
