# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli

from ...tests_api.tests_enforcements.test_enforcements import EnforcementsBase
from ...utils import load_clirunner


class TestGrpEnforcementsCmdUpdateOnCountIncreased(EnforcementsBase):
    def test_enable(self, request, monkeypatch, apiobj, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-on-count-increased",
                "--value",
                created_set_trigger.name,
                "--enable",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert "On Count Increased: True" in result.stdout

    def test_disable(self, request, monkeypatch, apiobj, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-on-count-increased",
                "--value",
                created_set_trigger.name,
                "--disable",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert "On Count Increased: False" in result.stdout
