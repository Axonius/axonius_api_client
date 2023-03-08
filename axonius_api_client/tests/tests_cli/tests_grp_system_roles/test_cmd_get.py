# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from ....cli import cli
from ...utils import load_clirunner
from .base import SystemRolesBase


class TestGrpSystemRolesCmdGet(SystemRolesBase):
    def test_json(self, apiobj, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "system",
                "roles",
                "get",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)

    @pytest.mark.parametrize("str_format", ["str", "str-args", "table"], scope="class")
    def test_str_types(self, apiobj, request, monkeypatch, str_format):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "system",
                "roles",
                "get",
                "--export-format",
                str_format,
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
