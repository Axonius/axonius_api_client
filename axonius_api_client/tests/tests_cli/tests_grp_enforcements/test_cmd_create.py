# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import json

import pytest

from axonius_api_client.cli import cli
from axonius_api_client.exceptions import ApiWarning
from axonius_api_client.tools import json_load

from ...tests_api.tests_enforcements.test_enforcements import EnforcementsBase, Meta
from ...utils import load_clirunner


class TestGrpEnforcementsCmdCreateDelete(EnforcementsBase):
    def test_config_stdin(self, request, monkeypatch, apiobj, device_sq_predefined):
        self.cleanup(apiobj=apiobj, value=Meta.name_cli)
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "enforcements",
                "create",
                "--name",
                Meta.name_cli,
                "--query-name",
                device_sq_predefined.name,
                "--main-action-name",
                Meta.action_name,
                "--main-action-type",
                Meta.action_type,
                "--export-format",
                "json",
            ]
            with pytest.warns(ApiWarning):
                result = runner.invoke(cli=cli, args=args, input=json.dumps(Meta.action_config))

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert Meta.name_cli in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

            args = [
                "enforcements",
                "delete",
                "--value",
                data["name"],
                "--export-format",
                "json",
            ]
            result = runner.invoke(
                cli=cli,
                args=args,
            )

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert Meta.name_cli in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

        self.cleanup(apiobj=apiobj, value=Meta.name_cli)

    def test_config_file(self, request, monkeypatch, apiobj, device_sq_predefined):
        self.cleanup(apiobj=apiobj, value=Meta.name_cli)
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            config = "config.json"
            with open(config, "w") as fh:
                json.dump(Meta.action_config, fh)

            args = [
                "enforcements",
                "create",
                "--name",
                Meta.name_cli,
                "--query-name",
                device_sq_predefined.name,
                "--main-action-name",
                Meta.action_name,
                "--main-action-type",
                Meta.action_type,
                "--main-action-config",
                config,
                "--export-format",
                "json",
            ]
            with pytest.warns(ApiWarning):
                result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert Meta.name_cli in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

            args = [
                "enforcements",
                "delete",
                "--value",
                data["name"],
                "--export-format",
                "json",
            ]
            result = runner.invoke(
                cli=cli,
                args=args,
            )

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert Meta.name_cli in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

        self.cleanup(apiobj=apiobj, value=Meta.name_cli)
