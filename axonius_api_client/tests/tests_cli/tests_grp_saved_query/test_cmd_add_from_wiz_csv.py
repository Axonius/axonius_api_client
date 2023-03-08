# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from ....cli import cli
from ...utils import load_clirunner
from .base import GrpSavedQueryDevices, GrpSavedQueryUsers


class GrpSavedQueryCmdAddFromWizCsv:
    pass


class TestDevicesGrpSavedQueryCmdAddFromWizCsv(GrpSavedQueryDevices, GrpSavedQueryCmdAddFromWizCsv):
    def test_add_success(self, apiobj, request, monkeypatch):
        runner = load_clirunner(request, monkeypatch)
        with runner.isolated_filesystem():
            result_csv = runner.invoke(
                cli=cli,
                args=[
                    apiobj.ASSET_TYPE,
                    "saved-query",
                    "add-from-wiz-csv",
                    "--help-detailed",
                    "wizard_csv",
                ],
            )
            content = result_csv.stderr.strip()

            args = [
                apiobj.ASSET_TYPE,
                "saved-query",
                "add-from-wiz-csv",
                "--no-abort",
                "--overwrite",
                "--export-format",
                "json",
            ]
            result = runner.invoke(cli=cli, args=args, input=content)
            data = self.check_result(result=result)

            exps = [
                "Initial parsing of supplied row successful",
                "Exporting successfully modified Saved Queries",
            ]
            missing = [x for x in exps if x not in result.stderr]
            assert not missing, missing

            for x in data:
                self._cleanup(apiobj=apiobj, value=x["name"])


class TestUsersGrpSavedQueryCmdAddFromWizCsv(GrpSavedQueryUsers, GrpSavedQueryCmdAddFromWizCsv):
    pass
