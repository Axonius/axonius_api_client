# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli

from ...tests_api.tests_enforcements.test_enforcements import EnforcementsBase
from ...utils import load_clirunner


class TestGrpEnforcementsCmdUpdateOnCountAbove(EnforcementsBase):
    def test_success(self, request, monkeypatch, apiobj, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-on-count-above",
                "--value",
                created_set_trigger.name,
                "--int",
                5,
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert "On Count Above: 5" in result.stdout

    def test_invalid_int(self, request, monkeypatch, apiobj, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-on-count-above",
                "--value",
                created_set_trigger.name,
                "--int",
                "invalid",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert not result.stdout
            assert result.stderr
            assert result.exit_code != 0
            assert "Supplied value 'invalid' of type str is not an integer." in result.stderr

    def test_none(self, request, monkeypatch, apiobj, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-on-count-above",
                "--value",
                created_set_trigger.name,
                "--int",
                "none",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert "On Count Above: None" in result.stdout
