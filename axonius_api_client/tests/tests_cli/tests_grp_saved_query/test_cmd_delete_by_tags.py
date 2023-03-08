# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ....tools import json_load
from ...utils import load_clirunner
from .base import FixtureData, GrpSavedQueryDevices, GrpSavedQueryUsers


class GrpSavedQueryCmdDeleteByTags:
    def test_json(self, apiobj, request, monkeypatch, sq_added):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args1 = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "delete-by-tags",
                "--export-format",
                "json",
            ]
            for tag in FixtureData.tags:
                args1 += ["--tag", tag]

            result1 = runner.invoke(cli=cli, args=args1)

            stderr1 = result1.stderr
            stdout1 = result1.stdout
            exit_code1 = result1.exit_code

            assert stdout1
            assert stderr1
            assert exit_code1 == 0

            json1 = json_load(stdout1)
            assert isinstance(json1, (dict, list))


class TestDevicesGrpSavedQueryCmdDeleteByTags(GrpSavedQueryDevices, GrpSavedQueryCmdDeleteByTags):
    pass


class TestUsersGrpSavedQueryCmdDeleteByTags(GrpSavedQueryUsers, GrpSavedQueryCmdDeleteByTags):
    pass
