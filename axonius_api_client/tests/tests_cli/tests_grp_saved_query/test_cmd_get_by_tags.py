# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import GrpSavedQueryDevices, GrpSavedQueryUsers


class GrpSavedQueryCmdGetByTags:
    def test_json(self, apiobj, request, monkeypatch, sq_tags):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "get-by-tags",
                "--export-format",
                "json",
            ]
            for tag in sq_tags[0:3]:
                args += ["--tag", tag]

            result = runner.invoke(cli=cli, args=args)
            self.check_result(result=result)


class TestDevicesGrpSavedQueryCmdGetByTags(GrpSavedQueryDevices, GrpSavedQueryCmdGetByTags):
    pass


class TestUsersGrpSavedQueryCmdGetByTags(GrpSavedQueryUsers, GrpSavedQueryCmdGetByTags):
    pass
