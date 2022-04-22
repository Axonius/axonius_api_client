# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""

from ....cli import cli
from ...utils import load_clirunner
from .base import DataScopesBase, Meta


class TestGrpDataScopesCmdCreate(DataScopesBase):
    def test_create_update_delete(
        self,
        apiobj,
        request,
        monkeypatch,
        f_asset_scope_users1,
        f_asset_scope_devices1,
        f_asset_scope_devices2,
    ):
        self.cleanup_data_scopes(apiobj=apiobj, value=Meta.names)
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            name = Meta.name
            args = [
                "system",
                "data-scopes",
                "create",
                "--name",
                name,
                "--device-scope",
                f_asset_scope_devices1.name,
                "--device-scope",
                f_asset_scope_devices2.name,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            name = self.check_result(result=result)["name"]

            args = [
                "system",
                "data-scopes",
                "update-description",
                "--value",
                name,
                "--update",
                "fooooooooo",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            name = self.check_result(result=result)["name"]

            args = [
                "system",
                "data-scopes",
                "update-name",
                "--value",
                name,
                "--update",
                Meta.name_update,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            name = self.check_result(result=result)["name"]

            args = [
                "system",
                "data-scopes",
                "update-user-scopes",
                "--value",
                name,
                "--update",
                f_asset_scope_users1.uuid,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            name = self.check_result(result=result)["name"]

            args = [
                "system",
                "data-scopes",
                "update-device-scopes",
                "--value",
                name,
                "--update",
                f_asset_scope_devices2.uuid,
                "--remove",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            name = self.check_result(result=result)["name"]

            args = [
                "system",
                "data-scopes",
                "delete",
                "--value",
                name,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)

        self.cleanup_data_scopes(apiobj=apiobj, value=Meta.names)
