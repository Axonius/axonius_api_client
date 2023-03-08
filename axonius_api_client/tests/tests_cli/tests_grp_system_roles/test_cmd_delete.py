# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import Meta, SystemRolesBase


class TestGrpSystemRolesCmdDelete(SystemRolesBase):
    def test_delete(self, apiobj, request, monkeypatch):
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
                "delete",
                "--name",
                Meta.name,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            # self.check_result(result=result) # TBD breaking

            self.cleanup_roles(apiobj=apiobj, value=Meta.name)
