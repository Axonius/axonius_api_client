# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli

from ...tests_api.tests_enforcements.test_enforcements import EnforcementsBase
from ...utils import load_clirunner


class TestGrpEnforcementsCmdUpdateScheduleMonthly(EnforcementsBase):
    def test_success(self, request, monkeypatch, apiobj, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-schedule-monthly",
                "--value",
                created_set_trigger.name,
                "--recurrence",
                "1,15,29",
                "--schedule-hour",
                "11",
                "--schedule-minute",
                "22",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            assert created_set_trigger.name in result.stdout
            assert "EnforcementSchedule Type: monthly" in result.stdout
            assert "EnforcementSchedule: 1st, 15th, Last Day at 11:22" in result.stdout

    def test_invalid_recurrence_bad_day_number(
        self, request, monkeypatch, apiobj, created_set_trigger
    ):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-schedule-monthly",
                "--value",
                created_set_trigger.name,
                "--recurrence",
                "29,30",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code != 0

            assert "Supplied value '30' is greater than max value of 29." in result.stderr

    def test_invalid_schedule_hour(self, request, monkeypatch, apiobj, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-schedule-monthly",
                "--value",
                created_set_trigger.name,
                "--recurrence",
                "1,15,29",
                "--schedule-hour",
                "25",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code != 0

            assert "Supplied value 25 is greater than max value of 23." in result.stderr

    def test_invalid_schedule_minute(self, request, monkeypatch, apiobj, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-schedule-monthly",
                "--value",
                created_set_trigger.name,
                "--recurrence",
                "1,15,29",
                "--schedule-minute",
                "61",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code != 0

            assert "Supplied value 61 is greater than max value of 59." in result.stderr
