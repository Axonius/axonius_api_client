# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import SystemRolesBase


class TestGrpSystemRolesCmdGetPerms(SystemRolesBase):
    def test_str_types(self, apiobj, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "system",
                "roles",
                "get-perms",
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
