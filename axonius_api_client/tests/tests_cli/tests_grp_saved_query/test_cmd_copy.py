# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""

from ....cli import cli
from ...utils import load_clirunner
from .base import GrpSavedQueryDevices

# , GrpSavedQueryUsers


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
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)
            self._cleanup(apiobj=apiobj, value=name)


class TestDevicesGrpSavedQueryCmdCopy(GrpSavedQueryDevices, GrpSavedQueryCmdCopy):
    pass


# class TestUsersGrpSavedQueryCmdCopy(GrpSavedQueryUsers, GrpSavedQueryCmdCopy):
#     pass
