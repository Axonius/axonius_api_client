# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import Meta, SystemRolesBase


class TestGrpSystemRolesCmdUpdateDataScope(SystemRolesBase):
    def test_update_data_scope(self, apiobj, request, monkeypatch, f_data_scope):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            self.cleanup_roles(apiobj=apiobj, value=Meta.name)
            args = [
                "system",
                "roles",
                "add",
                "--name",
                Meta.name,
                "--perm",
                "adapters=all",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)

            args = [
                "system",
                "roles",
                "update-data-scope",
                "--name",
                Meta.name,
                "--data-scope",
                f_data_scope.uuid,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)

            args = [
                "system",
                "roles",
                "update-data-scope",
                "--name",
                Meta.name,
                "--remove",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)

            self.cleanup_roles(apiobj=apiobj, value=Meta.name)
