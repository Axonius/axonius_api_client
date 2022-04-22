# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import Meta, SystemRolesBase


class TestGrpSystemRolesCmdUpdatePerms(SystemRolesBase):
    def test_update_perms(self, apiobj, request, monkeypatch):
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
                "update-perms",
                "--name",
                Meta.name,
                "--perm",
                "adapters=connections.delete,connections.post",
                "--deny",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)

            self.cleanup_roles(apiobj=apiobj, value=Meta.name)
