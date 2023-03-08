# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

from axonius_api_client.tools import json_dump

from ....cli import cli
from ...utils import load_clirunner
from .base import GrpSavedQueryDevices, GrpSavedQueryUsers


class GrpSavedQueryCmdAddFromJson:
    @pytest.mark.parametrize(
        "content, exps",
        [
            ["", ["Empty content supplied to '<stdin>'"]],
            ["1", ["required type is (<class 'list'>, <class 'dict'>)"]],
            ["{}", ["Missing required attribute 'name'"]],
            ['{"name": "xx"}', ["Missing required attribute 'view'"]],
        ],
    )
    def test_parsing_errors(self, apiobj, request, monkeypatch, content, exps):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "add-from-json",
                "--no-abort",
            ]
            result = runner.invoke(cli=cli, args=args, input=content)
            assert not result.stdout
            assert result.exit_code in [1, 100]
            missing = [x for x in exps if x not in result.stderr]
            assert not missing, missing

    def test_add_failure(self, apiobj, request, monkeypatch, sq_get):
        name = "fumfumfum"
        self._cleanup(apiobj=apiobj, value=name)

        data = sq_get.to_dict()
        data["view"] = {}
        data["name"] = name

        content = json_dump(data)
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "add-from-json",
                "--no-abort",
            ]
            result = runner.invoke(cli=cli, args=args, input=content)
            assert not result.stdout
            assert result.exit_code == 100

            exps = [
                "Initial parsing of supplied row successful",
                "Saved Query exists=False and overwrite=False, will create",
                "Create failed",
                "No changes made!",
            ]
            missing = [x for x in exps if x not in result.stderr]
            assert not missing, missing

        self._cleanup(apiobj=apiobj, value=name)

    @pytest.mark.skip("private sqs broken")
    def test_add_success(self, apiobj, request, monkeypatch, sq_get):
        name = "fumfumfum"
        self._cleanup(apiobj=apiobj, value=name)

        data = sq_get.to_dict()
        data["name"] = name

        content = json_dump(data)
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "add-from-json",
                "--no-abort",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args, input=content)
            self.check_result(result=result)

            exps = [
                "Initial parsing of supplied row successful",
                "Saved Query exists=False and overwrite=False, will create",
                "Create succeeded",
                "Exporting successfully modified Saved Queries",
            ]
            missing = [x for x in exps if x not in result.stderr]
            assert not missing, missing

        self._cleanup(apiobj=apiobj, value=name)

    def test_exists_overwrite_true_failure(self, apiobj, request, monkeypatch, sq_added):
        data = sq_added.to_dict()
        data["view"] = {}

        content = json_dump(data)
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "add-from-json",
                "--no-abort",
                "--overwrite",
            ]
            result = runner.invoke(cli=cli, args=args, input=content)
            assert not result.stdout
            assert result.exit_code == 100

            exps = [
                "Initial parsing of supplied row successful",
                "Saved Query exists=True and overwrite=True, will update",
                "Update failed",
                "No changes made!",
            ]
            missing = [x for x in exps if x not in result.stderr]
            assert not missing, missing

    def test_exists_overwrite_false(self, apiobj, request, monkeypatch, sq_added):
        content = json_dump(sq_added)
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "add-from-json",
                "--no-abort",
                "--no-overwrite",
            ]
            result = runner.invoke(cli=cli, args=args, input=content)
            assert not result.stdout
            assert result.exit_code == 100

            exps = [
                "Initial parsing of supplied row successful",
                "Saved Query exists=True and overwrite=False, can not update",
                "No changes made!",
            ]
            missing = [x for x in exps if x not in result.stderr]
            assert not missing, missing

    def test_exists_overwrite_true(self, apiobj, request, monkeypatch, sq_added):
        content = json_dump(sq_added)
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "add-from-json",
                "--no-abort",
                "--overwrite",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args, input=content)
            self.check_result(result=result)

            exps = [
                "Initial parsing of supplied row successful",
                "Saved Query exists=True and overwrite=True, will update",
                "Update succeeded",
            ]
            missing = [x for x in exps if x not in result.stderr]
            assert not missing, missing


class TestDevicesGrpSavedQueryCmdAddFromJson(GrpSavedQueryDevices, GrpSavedQueryCmdAddFromJson):
    pass


class TestUsersGrpSavedQueryCmdAddFromJson(GrpSavedQueryUsers, GrpSavedQueryCmdAddFromJson):
    pass
