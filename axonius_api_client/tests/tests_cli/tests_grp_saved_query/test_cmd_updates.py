# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from axonius_api_client.constants.api import GUI_PAGE_SIZES

from ....cli import cli
from ...utils import load_clirunner
from .base import GrpSavedQueryDevices, GrpSavedQueryUsers


class GrpSavedQueryCmdUpdates:
    def test_cmd_update_always_cached(self, apiobj, request, monkeypatch, sq_added):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "update-always-cached",
                "--saved-query",
                sq_added.name,
                "--value",
                "y",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            data = self.check_result(result=result)
            assert data["always_cached"] is True

    def test_cmd_update_page_size(self, apiobj, request, monkeypatch, sq_added):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "update-page-size",
                "--saved-query",
                sq_added.name,
                "--value",
                f"{GUI_PAGE_SIZES[1]}",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            data = self.check_result(result=result)
            assert data["view"]["pageSize"] == GUI_PAGE_SIZES[1]

    def test_cmd_update_private(self, apiobj, request, monkeypatch, sq_added):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "update-private",
                "--saved-query",
                sq_added.name,
                "--value",
                "y",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.exit_code != 0
            assert "Can't change a public query to be a private query." in result.stderr

    def test_cmd_update_name_success(self, apiobj, request, monkeypatch, sq_added):
        value_new = "manananlskafdjl"
        self._cleanup(apiobj=apiobj, value=value_new)

        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "update-name",
                "--saved-query",
                sq_added.name,
                "--value",
                value_new,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            data = self.check_result(result=result)
            assert data["name"] == value_new
        self._cleanup(apiobj=apiobj, value=value_new)

    def test_cmd_update_name_failure_exists(self, apiobj, request, monkeypatch, sq_added):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "update-name",
                "--saved-query",
                sq_added.name,
                "--value",
                sq_added.name,
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert not result.stdout
            assert result.exit_code == 1
            exp = f"Saved query with name or uuid of {sq_added.name!r} already exists"
            assert exp in result.stderr

    def test_cmd_update_description(self, apiobj, request, monkeypatch, sq_added):
        runner = load_clirunner(request, monkeypatch)
        value_new = "new description"
        value_append = "\nmore newness"
        value_append_exp = value_new + value_append

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli=cli,
                args=[
                    apiobj.ASSET_TYPE,
                    "saved-query",
                    "update-description",
                    "--saved-query",
                    sq_added.name,
                    "--value",
                    value_new,
                    "--export-format",
                    "json",
                ],
            )
            data = self.check_result(result=result)
            assert data["description"] == value_new

            result = runner.invoke(
                cli=cli,
                args=[
                    apiobj.ASSET_TYPE,
                    "saved-query",
                    "update-description",
                    "--saved-query",
                    sq_added.name,
                    "--value",
                    value_append,
                    "--append",
                    "--export-format",
                    "json",
                ],
            )
            data = self.check_result(result=result)
            assert data["description"] == value_append_exp

    def test_cmd_update_tags(self, apiobj, request, monkeypatch, sq_added):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli=cli,
                args=[
                    apiobj.ASSET_TYPE,
                    "saved-query",
                    "update-tags",
                    "--saved-query",
                    sq_added.name,
                    "--value",
                    "tag1",
                    "--value",
                    "tag2",
                    "--export-format",
                    "json",
                ],
            )
            data = self.check_result(result=result)
            tags = data["tags"]
            assert tags == ["tag1", "tag2"]

            result = runner.invoke(
                cli=cli,
                args=[
                    apiobj.ASSET_TYPE,
                    "saved-query",
                    "update-tags",
                    "--saved-query",
                    sq_added.name,
                    "--value",
                    "tag3",
                    "--value",
                    "tag4",
                    "--append",
                    "--export-format",
                    "json",
                ],
            )
            data = self.check_result(result=result)
            tags = data["tags"]
            assert tags == ["tag1", "tag2", "tag3", "tag4"]

            result = runner.invoke(
                cli=cli,
                args=[
                    apiobj.ASSET_TYPE,
                    "saved-query",
                    "update-tags",
                    "--saved-query",
                    sq_added.name,
                    "--value",
                    "tag3",
                    "--remove",
                    "--export-format",
                    "json",
                ],
            )
            data = self.check_result(result=result)
            tags = data["tags"]
            assert tags == ["tag1", "tag2", "tag4"]


class TestDevicesGrpSavedQueryCmdUpdates(GrpSavedQueryDevices, GrpSavedQueryCmdUpdates):
    def test_cmd_update_query(self, apiobj, request, monkeypatch, sq_added):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli=cli,
                args=[
                    apiobj.ASSET_TYPE,
                    "saved-query",
                    "update-query",
                    "--saved-query",
                    sq_added.name,
                    "--wiz",
                    "simple",
                    "os.type equals windows",
                    "--export-format",
                    "json",
                ],
            )
            data = self.check_result(result=result)
            query = data["view"]["query"]["filter"]
            exps = ["os.type"]
            missing = [x for x in exps if x not in query]
            assert not missing, missing

            result = runner.invoke(
                cli=cli,
                args=[
                    apiobj.ASSET_TYPE,
                    "saved-query",
                    "update-query",
                    "--saved-query",
                    sq_added.name,
                    "--wiz",
                    "simple",
                    "hostname contains test",
                    "--append",
                    "--append-and-flag",
                    "--append-not-flag",
                    "--export-format",
                    "json",
                ],
            )
            data = self.check_result(result=result)
            query = data["view"]["query"]["filter"]
            exps = ["os.type", "hostname", " and ", " not "]
            missing = [x for x in exps if x not in query]
            assert not missing, missing

    def test_cmd_update_fields(self, apiobj, request, monkeypatch, sq_added):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli=cli,
                args=[
                    apiobj.ASSET_TYPE,
                    "saved-query",
                    "update-fields",
                    "--saved-query",
                    sq_added.name,
                    "--field",
                    "os.type",
                    "--export-format",
                    "json",
                ],
            )
            data = self.check_result(result=result)
            fields = data["view"]["fields"]
            assert fields == ["specific_data.data.os.type"]

            result = runner.invoke(
                cli=cli,
                args=[
                    apiobj.ASSET_TYPE,
                    "saved-query",
                    "update-fields",
                    "--saved-query",
                    sq_added.name,
                    "--field",
                    "hostname",
                    "--append",
                    "--export-format",
                    "json",
                ],
            )
            data = self.check_result(result=result)
            fields = data["view"]["fields"]
            assert fields == ["specific_data.data.os.type", "specific_data.data.hostname"]

            result = runner.invoke(
                cli=cli,
                args=[
                    apiobj.ASSET_TYPE,
                    "saved-query",
                    "update-fields",
                    "--saved-query",
                    sq_added.name,
                    "--field",
                    "os.type",
                    "--remove",
                    "--export-format",
                    "json",
                ],
            )
            data = self.check_result(result=result)
            fields = data["view"]["fields"]
            assert fields == ["specific_data.data.hostname"]


class TestUsersGrpSavedQueryCmdUpdates(GrpSavedQueryUsers, GrpSavedQueryCmdUpdates):
    pass
