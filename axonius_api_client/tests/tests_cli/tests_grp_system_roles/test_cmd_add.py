# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import Meta, SystemRolesBase


class TestGrpSystemRolesCmdAdd(SystemRolesBase):
    def test_add(self, apiobj, request, monkeypatch):
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
            self.cleanup_roles(apiobj=apiobj, value=Meta.name)

    def test_add_data_scope(self, apiobj, request, monkeypatch, f_data_scope):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            name = "badwolf CLI data scope"
            self.cleanup_roles(apiobj=apiobj, value=name)
            args = [
                "system",
                "roles",
                "add",
                "--name",
                name,
                "--perm",
                "adapters=all",
                "--data-scope",
                f_data_scope.uuid,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)
            self.cleanup_roles(apiobj=apiobj, value=name)
