# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import GrpSavedQueryDevices, GrpSavedQueryUsers


class GrpSavedQueryCmdCopy:
    def test_success(self, apiobj, request, monkeypatch, sq_get):
        name = "manannanaa"
        self._cleanup(apiobj=apiobj, value=name)

        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "copy",
                "--saved-query",
                sq_get.name,
                "--name",
                name,
                "--private",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            data = self.check_result(result=result)
            assert data["private"] is True
            self._cleanup(apiobj=apiobj, value=name)

    def test_failure_name_exists(self, apiobj, request, monkeypatch, sq_get):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "copy",
                "--saved-query",
                sq_get.name,
                "--name",
                sq_get.name,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert not result.stdout
            assert result.exit_code == 1
            assert (
                f"Saved query with name or uuid of '{sq_get.name}' already exists" in result.stderr
            )


class TestDevicesGrpSavedQueryCmdCopy(GrpSavedQueryDevices, GrpSavedQueryCmdCopy):
    pass


class TestUsersGrpSavedQueryCmdCopy(GrpSavedQueryUsers, GrpSavedQueryCmdCopy):
    pass
