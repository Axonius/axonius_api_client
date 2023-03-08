# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from ....cli import cli
from ...utils import load_clirunner
from .base import DataScopesBase


class TestGrpDataScopesCmdGet(DataScopesBase):
    def test_json(self, apiobj, request, monkeypatch, f_data_scope):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "system",
                "data-scopes",
                "get",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)

    @pytest.mark.parametrize("str_format", ["str", "table"], scope="class")
    def test_str_types(self, apiobj, request, monkeypatch, str_format, f_data_scope):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "system",
                "data-scopes",
                "get",
                "--export-format",
                str_format,
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

    def test_json_value(self, apiobj, request, monkeypatch, f_data_scope):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "system",
                "data-scopes",
                "get",
                "--value",
                f_data_scope.uuid,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)

    @pytest.mark.parametrize("str_format", ["str", "table"], scope="class")
    def test_str_types_value(self, apiobj, request, monkeypatch, str_format, f_data_scope):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                "system",
                "data-scopes",
                "get",
                "--value",
                f_data_scope.uuid,
                "--export-format",
                str_format,
            ]
            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
