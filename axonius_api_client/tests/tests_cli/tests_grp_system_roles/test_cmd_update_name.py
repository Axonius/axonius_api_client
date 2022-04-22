# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import Meta, SystemRolesBase


class TestGrpSystemRolesCmdUpdateName(SystemRolesBase):
    def test_update_name(self, apiobj, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            self.cleanup_roles(apiobj=apiobj, value=Meta.names)
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
                "update-name",
                "--name",
                Meta.name,
                "--new-name",
                Meta.name_update,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)

            self.cleanup_roles(apiobj=apiobj, value=Meta.names)
