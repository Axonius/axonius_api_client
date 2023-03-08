# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import GrpSavedQueryDevices, GrpSavedQueryUsers


class GrpSavedQueryCmdGetByName:
    def test_json(self, apiobj, request, monkeypatch, sq_get):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "get-by-name",
                "--name",
                sq_get.name,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)


class TestDevicesGrpSavedQueryCmdGetByName(GrpSavedQueryDevices, GrpSavedQueryCmdGetByName):
    pass


class TestUsersGrpSavedQueryCmdGetByName(GrpSavedQueryUsers, GrpSavedQueryCmdGetByName):
    pass
