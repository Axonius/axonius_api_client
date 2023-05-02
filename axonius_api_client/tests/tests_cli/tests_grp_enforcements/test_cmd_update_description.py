# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli

from ...tests_api.tests_enforcements.test_enforcements import EnforcementsBase
from ...utils import load_clirunner


class TestGrpEnforcementsCmdUpdateDescription(EnforcementsBase):
    def test_success(self, request, monkeypatch, apiobj, created_set_trigger):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            description = "set description"
            args = [
                "enforcements",
                "update-description",
                "--value",
                created_set_trigger.name,
                "--description",
                description,
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            assert description in result.stdout

            added = "added to description"
            args = [
                "enforcements",
                "update-description",
                "--value",
                created_set_trigger.name,
                "--description",
                added,
                "--append",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

            assert added in result.stdout
            assert description in result.stdout
