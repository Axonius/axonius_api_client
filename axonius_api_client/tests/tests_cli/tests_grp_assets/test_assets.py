# -*- coding: utf-8 -*-
"""Test suite."""
import pytest

from axonius_api_client.cli import cli
from axonius_api_client.tools import json_load

from ...utils import get_rows_exist, load_clirunner


class GrpAssetsBase:
    @pytest.fixture(scope="class")
    def existing_sq(self, apiobj):
        return apiobj.saved_query.get(as_dataclass=True)[0]

    def check_count_result(self, result):
        assert result.stdout
        assert result.stderr
        assert result.exit_code == 0
        value = int(result.stdout)
        assert isinstance(value, int)

    def check_get_result(self, result):
        assert result.stdout
        assert result.stderr
        assert result.exit_code == 0
        data = json_load(result.stdout)
        assert isinstance(data, list)
        assert len(data) <= 2
        for item in data:
            assert isinstance(item, dict)

    def test_count(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "count",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_count_result(result)

    def test_count_wiz(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "count",
                "--wiz",
                "simple",
                f'"{apiobj.FIELD_SIMPLE} contains test',
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_count_result(result)

    def test_count_history_days_ago(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "count",
                "--history-days-ago",
                "1",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_count_result(result)

    def test_count_by_saved_query(self, request, monkeypatch, existing_sq, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "count-by-saved-query",
                "--name",
                f"{existing_sq.name}",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_count_result(result)

    def test_get_by_id(self, request, monkeypatch, apiobj):
        asset = get_rows_exist(apiobj=apiobj)
        get_id = asset["internal_axon_id"]
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-by-id",
                "--id",
                f"{get_id}",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            data = json_load(result.stdout)
            assert isinstance(data, dict) and data

    def test_get_by_saved_query(self, request, monkeypatch, existing_sq, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-by-saved-query",
                "--name",
                f"{existing_sq.name}",
                "--max-rows",
                "2",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_get_result(result=result)

    @pytest.mark.parametrize("export_format", ["str", "table"])
    def test_get_fields_export_str_types(self, request, monkeypatch, export_format, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-fields",
                "--export-format",
                export_format,
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

    @pytest.mark.parametrize("export_format", ["json", "json-full"])
    def test_get_fields_export_json_types(self, request, monkeypatch, export_format, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-fields",
                "--export-format",
                export_format,
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            data = json_load(result.stdout)
            assert isinstance(data, list) and data
            for item in data:
                assert isinstance(item, dict)

    def test_get_fields_match_adapter_re(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-fields",
                "--export-format",
                "str",
                "-ar",
                "^a.*",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            for line in result.stdout.splitlines():
                assert line.startswith("a")

    def test_get_fields_match_root_only(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-fields",
                "--export-format",
                "str",
                "--root-only",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            exp = f"{apiobj.FIELD_COMPLEX}.{apiobj.FIELD_COMPLEX_SUB}"
            assert exp not in result.stdout

    def test_get_fields_match_no_complex(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-fields",
                "--export-format",
                "str",
                "--no-include-complex",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            exp = f"{apiobj.FIELD_COMPLEX}"
            assert exp not in result.stdout

    def test_get_fields_match_no_simple(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-fields",
                "--export-format",
                "str",
                "--no-include-simple",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            exp = f"{apiobj.FIELD_SIMPLE}"
            assert exp not in result.stdout

    def test_get_fields_match_no_agg(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-fields",
                "--export-format",
                "str",
                "--no-include-agg",
                "--adapter-re",
                "^csv$",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0
            exp = f"csv:{apiobj.FIELD_SIMPLE}"
            assert exp not in result.stdout

    def test_get_fields_default(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-fields-default",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

    def test_get_tags(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-tags",
            ]
            result = runner.invoke(cli=cli, args=args)
            assert result.stdout
            assert result.stderr
            assert result.exit_code == 0

    def test_get_json(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get",
                "--max-rows",
                "2",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_get_result(result=result)

    def test_destroy(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            disable_destroy_args = [
                "system",
                "settings-global",
                "configure-destroy",
                "--enable",
                "--no-destroy",
                "--no-reset",
            ]

            fail_not_enabled_args = [
                apiobj.ASSET_TYPE,
                "destroy",
                "--destroy",
                "--no-history",
            ]

            enable_destroy_args = [
                "system",
                "settings-global",
                "configure-destroy",
                "--enable",
                "--destroy",
                "--no-reset",
            ]

            fail_destroy_false_args = [
                apiobj.ASSET_TYPE,
                "destroy",
                "--no-destroy",
                "--no-history",
            ]

            disable_destroy = runner.invoke(cli=cli, args=disable_destroy_args)
            assert disable_destroy.stdout
            assert disable_destroy.stderr
            assert disable_destroy.exit_code == 0

            fail_not_enabled = runner.invoke(cli=cli, args=fail_not_enabled_args)
            assert not fail_not_enabled.stdout
            assert fail_not_enabled.stderr
            assert fail_not_enabled.exit_code == 1
            assert "Enable API Destroy Endpoints must be enabled" in fail_not_enabled.stderr

            enable_destroy = runner.invoke(cli=cli, args=enable_destroy_args)
            assert enable_destroy.stdout
            assert enable_destroy.stderr
            assert enable_destroy.exit_code == 0

            fail_destroy_false = runner.invoke(cli=cli, args=fail_destroy_false_args)
            assert not fail_destroy_false.stdout
            assert fail_destroy_false.stderr
            assert fail_destroy_false.exit_code == 1
            assert "Must supply destroy=True" in fail_destroy_false.stderr

            disable_destroy = runner.invoke(cli=cli, args=disable_destroy_args)
            assert disable_destroy.stdout
            assert disable_destroy.stderr
            assert disable_destroy.exit_code == 0


class TestGrpAssetsDevices(GrpAssetsBase):
    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        return api_devices

    def test_get_by_hostname(self, request, monkeypatch, apiobj):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():

            args = [
                apiobj.ASSET_TYPE,
                "get-by-hostname-re",
                "--value",
                "test",
                "--max-rows",
                "2",
            ]
            result = runner.invoke(cli=cli, args=args)
            self.check_get_result(result=result)


class TestGrpAssetsUsers(GrpAssetsBase):
    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        return api_users
