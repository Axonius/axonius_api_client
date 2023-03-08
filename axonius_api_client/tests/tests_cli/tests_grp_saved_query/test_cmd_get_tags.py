# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import GrpSavedQueryDevices, GrpSavedQueryUsers


class GrpSavedQueryCmdGetTags:
    def test_str(self, apiobj, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "get-tags",
            ]

            result = runner.invoke(cli=cli, args=args)

            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0


class TestDevicesGrpSavedQueryCmdGetTags(GrpSavedQueryDevices, GrpSavedQueryCmdGetTags):
    pass


class TestUsersGrpSavedQueryCmdGetTags(GrpSavedQueryUsers, GrpSavedQueryCmdGetTags):
    pass
