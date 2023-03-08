# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import FixtureData, GrpSavedQueryDevices  # , GrpSavedQueryUsers


class GrpSavedQueryCmdAdd:
    def test_add(self, apiobj, request, monkeypatch):
        self._cleanup(apiobj=apiobj, value=FixtureData.add_name)

        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "add",
                "--name",
                FixtureData.add_name,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)
            self._cleanup(apiobj=apiobj, value=FixtureData.add_name)


class TestDevicesGrpSavedQueryCmdAdd(GrpSavedQueryDevices, GrpSavedQueryCmdAdd):
    pass


# class TestUsersGrpSavedQueryCmdAdd(GrpSavedQueryUsers, GrpSavedQueryCmdAdd):
#     pass
