# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli

from ...tests_api.tests_enforcements.test_enforcements import EnforcementsBase
from ...utils import load_clirunner
import random


class TestGrpEnforcementsCmdUpdateQuery(EnforcementsBase):
    def test_success(self, request, monkeypatch, apiobj, api_devices, created_set_trigger):
        new_sq = random.choice(
            [x for x in api_devices.saved_query.get(as_dataclass=True) if x.predefined]
        )
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "update-query",
                "--value",
                created_set_trigger.name,
                "--query-name",
                new_sq.name,
                "--query-type",
                new_sq.module,
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert new_sq.name in result.stdout
