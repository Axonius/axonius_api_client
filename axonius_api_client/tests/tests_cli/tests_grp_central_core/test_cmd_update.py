# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load

from ...utils import load_clirunner


class TestGrpCentralCoreCmdUpdate:
    def test_update(self, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            get_args = [
                "system",
                "central-core",
                "get",
            ]
            get_result = runner.invoke(cli=cli, args=get_args)

            assert get_result.stdout
            assert get_result.stderr
            assert get_result.exit_code == 0

            get_data = json_load(get_result.stdout)
            assert isinstance(get_data, dict) and get_data

            enabled_orig = get_data["enabled"]
            delete_orig = get_data["delete_backups"]

            enabled_update = "--enable" if not enabled_orig else "--no-enable"
            delete_update = "--delete-backups" if not delete_orig else "--no-delete-backups"

            update_args = [
                "system",
                "central-core",
                "update",
                enabled_update,
                delete_update,
            ]
            update_result = runner.invoke(cli=cli, args=update_args)

            assert update_result.stdout
            assert update_result.stderr
            assert update_result.exit_code == 0

            update_data = json_load(update_result.stdout)
            assert isinstance(update_data, dict) and update_data

            enabled_updated = update_data["enabled"]
            delete_updated = update_data["delete_backups"]

            assert enabled_updated is not enabled_orig
            assert delete_updated is not delete_orig

            enabled_revert = "--enable" if enabled_orig else "--no-enable"
            delete_revert = "--delete-backups" if delete_orig else "--no-delete-backups"

            revert_args = [
                "system",
                "central-core",
                "update",
                enabled_revert,
                delete_revert,
            ]
            revert_result = runner.invoke(cli=cli, args=revert_args)

            assert revert_result.stdout
            assert revert_result.stderr
            assert revert_result.exit_code == 0

            revert_data = json_load(revert_result.stdout)
            assert isinstance(revert_data, dict) and revert_data

            enabled_reverted = revert_data["enabled"]
            delete_reverted = revert_data["delete_backups"]
            assert enabled_reverted == enabled_orig
            assert delete_reverted == delete_orig
