# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import json

import pytest

from axonius_api_client.cli import cli
from axonius_api_client.exceptions import ApiWarning
from axonius_api_client.tools import json_load

from ...tests_api.tests_enforcements.test_enforcements import EnforcementsBase, Meta
from ...utils import load_clirunner


class TestGrpEnforcementsCmdCopyUpdate(EnforcementsBase):
    def test_multi(self, request, monkeypatch, apiobj, created_set_trigger):
        self.cleanup(apiobj=apiobj, value=Meta.name_copy)
        self.cleanup(apiobj=apiobj, value=Meta.name_rename_cli)

        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            # COPY
            args = [
                "enforcements",
                "copy",
                "--value",
                created_set_trigger.name,
                "--name",
                Meta.name_copy,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert Meta.name_copy in result.stdout
            assert created_set_trigger.name not in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

            # RENAME
            args = [
                "enforcements",
                "update-name",
                "--value",
                data["uuid"],
                "--name",
                Meta.name_rename_cli,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert Meta.name_rename_cli in result.stdout
            assert Meta.name_copy not in result.stdout
            assert created_set_trigger.name not in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

            # update main action
            args = [
                "enforcements",
                "update-action-main",
                "--value",
                data["uuid"],
                "--name",
                Meta.action_name2,
                "--type",
                Meta.action_type,
                "--export-format",
                "json",
            ]
            with pytest.warns(ApiWarning):
                result = runner.invoke(cli=cli, args=args, input=json.dumps(Meta.action_config))

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert data["uuid"] in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

            # add success action
            args = [
                "enforcements",
                "update-action-add",
                "--value",
                data["uuid"],
                "--category",
                "success",
                "--name",
                "leafy",
                "--type",
                Meta.action_type,
                "--export-format",
                "json",
            ]
            with pytest.warns(ApiWarning):
                result = runner.invoke(cli=cli, args=args, input=json.dumps(Meta.action_config))

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert data["uuid"] in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

            # remove success action
            args = [
                "enforcements",
                "update-action-remove",
                "--value",
                data["uuid"],
                "--category",
                "success",
                "--name",
                "leafy",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            assert data["uuid"] in result.stdout

            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

        self.cleanup(apiobj=apiobj, value=Meta.name_copy)
        self.cleanup(apiobj=apiobj, value=Meta.name_rename_cli)
