# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from axonius_api_client import api, cli, tools

from .. import utils


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCliGrpObjectsCmdCount(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args = [
            cmd,
            "count",
            "--query",
            "(adapters > size(0))",
            "--export-format",
            "json",
        ]

        result = runner.invoke(cli=cli.cli, args=args)

        assert result.exit_code == 0

        json_stdout = tools.json_load(result.stdout)
        assert isinstance(json_stdout, tools.INT)


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCliGrpObjectCmdFields(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli, args=[cmd, "fields", "--export-format", "json"]
        )

        assert result.exit_code == 0

        json_reloaded = tools.json_load(result.stdout)
        assert isinstance(json_reloaded, dict)

    def test_csv(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli, args=[cmd, "fields", "--export-format", "csv"]
        )

        assert result.exit_code == 0
        utils.check_csv_cols(result.stdout, ["generic"])

    def test_get_exc_wrap(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        monkeypatch.setattr(api.users_devices.Fields, "get", utils.mock_failure)

        result = runner.invoke(cli=cli.cli, args=[cmd, "fields"])

        assert result.exit_code != 0
        stderr = result.stderr.splitlines()
        assert len(stderr) == 4
        assert (
            stderr[-2]
            == "** ERROR: WRAPPED EXCEPTION: axonius_api_client.tests.utils.MockError"
        )
        assert stderr[-1] == "badwolf"

    def test_get_exc_nowrap(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        monkeypatch.setattr(api.users_devices.Fields, "get", utils.mock_failure)

        with pytest.raises(utils.MockError):
            runner.invoke(
                cli=cli.cli,
                args=["--no-wraperror", cmd, "fields"],
                catch_exceptions=False,
            )

    def test_adapter_re(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli, args=[cmd, "fields", "--adapter-re", "generic"]
        )

        assert result.exit_code == 0

        json_reloaded = tools.json_load(result.stdout)
        assert isinstance(json_reloaded, dict)
        assert list(json_reloaded) == ["generic"]

    def test_adapter_fields_re(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli,
            args=[cmd, "fields", "--adapter-re", "generic", "--field-re", "name"],
        )

        assert result.exit_code == 0, result.stderr

        json_reloaded = tools.json_load(result.stdout)
        assert isinstance(json_reloaded, dict)
        for k, v in json_reloaded.items():
            assert k == "generic"
            for i in v:
                assert "name" in i

    def test_adapter_fields_re_err(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        result = runner.invoke(
            cli=cli.cli,
            args=[cmd, "fields", "--adapter-re", "generic", "--field-re", "badwolf"],
        )
        assert result.exit_code != 0
        stderr = result.stderr.splitlines()
        assert stderr[-1].startswith("** ERROR: No fields found matching ")


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCliGrpObjectsCmdGet(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args = [
            cmd,
            "get",
            "--query",
            "(adapters > size(0))",
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        result = runner.invoke(cli=cli.cli, args=args)

        assert result.exit_code == 0

        json_stdout = tools.json_load(result.stdout)
        assert isinstance(json_stdout, tools.LIST)

    def test_csv(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        if cmd == "devices":
            args = [
                cmd,
                "get",
                "--query",
                '((specific_data.data.installed_software == ({"$exists":true,"$ne":""})))',  # noqa
                "--field",
                "installed_software",
                "--export-format",
                "csv",
                "--max-rows",
                "1",
            ]
        else:
            args = [
                cmd,
                "get",
                "--query",
                "(adapters > size(0))",
                "--export-format",
                "csv",
                "--max-rows",
                "1",
            ]

        result = runner.invoke(cli=cli.cli, args=args)

        assert result.exit_code == 0

        utils.check_csv_cols(result.stdout, ["internal_axon_id"])

    def test_csv_complex(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        args = [
            cmd,
            "get",
            "--query",
            "(adapters > size(0))",
            "--field",
            "all",
            "--export-format",
            "csv",
            "--max-rows",
            "1",
        ]

        result = runner.invoke(cli=cli.cli, args=args)

        stderr = result.stderr
        stdout = result.stdout
        exit_code = result.exit_code

        assert exit_code == 0, stderr

        utils.check_csv_cols(stdout, ["internal_axon_id"])


class TestCliGrpObjectsCmdGetBySubnet(object):
    """Pass."""

    def test_json(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args = [
            "devices",
            "get-by-subnet",
            "--value",
            "10.0.0.0/8",
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        result = runner.invoke(cli=cli.cli, args=args)

        assert result.exit_code == 0

        json_stdout = tools.json_load(result.stdout)
        assert isinstance(json_stdout, tools.LIST)

    def test_csv(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args = [
            "devices",
            "get-by-subnet",
            "--value",
            "10.0.0.0/8",
            "--export-format",
            "csv",
            "--max-rows",
            "1",
        ]

        result = runner.invoke(cli=cli.cli, args=args)

        assert result.exit_code == 0

        utils.check_csv_cols(result.stdout, ["internal_axon_id"])


@pytest.mark.parametrize("get_by", ["get-by-hostname", "get-by-ip", "get-by-mac"])
class TestCliGrpObjectsCmdGetByDevices(object):
    """Pass."""

    def test_json(self, request, monkeypatch, get_by):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args = [
            "devices",
            get_by,
            "--value",
            "RE:.*",
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        result = runner.invoke(cli=cli.cli, args=args)

        assert result.exit_code == 0

        json_stdout = tools.json_load(result.stdout)
        assert isinstance(json_stdout, tools.LIST)

    def test_csv(self, request, monkeypatch, get_by):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args = [
            "devices",
            get_by,
            "--value",
            "RE:.*",
            "--export-format",
            "csv",
            "--max-rows",
            "1",
        ]

        result = runner.invoke(cli=cli.cli, args=args)

        assert result.exit_code == 0

        utils.check_csv_cols(result.stdout, ["internal_axon_id"])


@pytest.mark.parametrize("get_by", ["get-by-mail", "get-by-username"])
class TestCliGrpObjectsCmdGetByUsers(object):
    """Pass."""

    def test_json(self, request, monkeypatch, get_by):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args = [
            "users",
            get_by,
            "--value",
            "RE:.*",
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        result = runner.invoke(cli=cli.cli, args=args)

        assert result.exit_code == 0

        json_stdout = tools.json_load(result.stdout)
        assert isinstance(json_stdout, tools.LIST)

    def test_csv(self, request, monkeypatch, get_by):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args = [
            "users",
            get_by,
            "--value",
            "RE:.*",
            "--export-format",
            "csv",
            "--max-rows",
            "1",
        ]

        result = runner.invoke(cli=cli.cli, args=args)

        assert result.exit_code == 0

        utils.check_csv_cols(result.stdout, ["internal_axon_id"])
