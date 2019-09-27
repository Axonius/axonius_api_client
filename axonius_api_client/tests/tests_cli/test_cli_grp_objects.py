# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from axonius_api_client import api, cli, tools

from .. import utils


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCmdCount(object):
    """Pass."""

    def test_query_file(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        qf_contents = '(adapters == "aws_adapter")'
        qf_file = "qf.txt"

        args1 = [cmd, "count", "--query-file", qf_file]

        with runner.isolated_filesystem():
            with open(qf_file, "w") as f:
                f.write(qf_contents)

            result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(result1.stdout)
        assert isinstance(json1, tools.INT)

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "count", "--query", "(adapters > size(0))"]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(result1.stdout)
        assert isinstance(json1, tools.INT)


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCmdCountBySQ(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "saved-query", "get"]
        result1 = runner.invoke(cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

        name = json1[0]["name"]

        args2 = [cmd, "count-by-saved-query", "--name", name]

        result2 = runner.invoke(cli=cli.cli, args=args2)

        exit_code2 = result2.exit_code
        stdout2 = result2.stdout
        stderr2 = result2.stderr

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.INT)


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCmdGetBySQ(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "saved-query", "get"]
        result1 = runner.invoke(cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)

        assert isinstance(json1, tools.LIST)
        name = json1[0]["name"]

        args2 = [cmd, "get-by-saved-query", "--name", name, "--max-rows", "1"]

        result2 = runner.invoke(cli=cli.cli, args=args2)

        exit_code2 = result2.exit_code
        stdout2 = result2.stdout
        stderr2 = result2.stderr

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.LIST)


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCmdFields(object):
    """Pass."""

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "fields", "--export-format", "json"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, dict)

    def test_csv(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "fields", "--export-format", "csv"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        utils.check_csv_cols(stdout1, ["generic"])

    def test_get_exc_wrap(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        monkeypatch.setattr(api.users_devices.Fields, "get", utils.mock_failure)

        args1 = [cmd, "fields"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert not stdout1
        assert stderr1
        assert exit_code1 != 0

        errlines1 = stderr1.splitlines()

        assert (
            errlines1[-2]
            == "** ERROR: WRAPPED EXCEPTION: axonius_api_client.tests.utils.MockError"
        )
        assert errlines1[-1] == "badwolf"

    def test_get_exc_nowrap(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        monkeypatch.setattr(api.users_devices.Fields, "get", utils.mock_failure)
        args1 = ["--no-wraperror", cmd, "fields"]
        with pytest.raises(utils.MockError):
            runner.invoke(cli=cli.cli, args=args1, catch_exceptions=False)

    def test_adapter_re(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "fields", "--adapter-re", "generic"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, dict)
        assert list(json1) == ["generic"]

    def test_adapter_fields_re(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "fields", "--adapter-re", "generic", "--field-re", "name"]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, dict)
        for k, v in json1.items():
            assert k == "generic"
            for i in v:
                assert "name" in i

    def test_adapter_fields_re_err(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [cmd, "fields", "--adapter-re", "generic", "--field-re", "badwolf"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert not stdout1
        assert stderr1
        assert exit_code1 != 0

        errlines1 = stderr1.splitlines()
        assert errlines1[-1].startswith("** ERROR: No fields found matching ")


@pytest.mark.parametrize("cmd", ["devices", "users"])
class TestCmdGet(object):
    """Pass."""

    def test_query_file(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        qf_contents = '(adapters == "aws_adapter")'
        qf_file = "qf.txt"

        args1 = [
            cmd,
            "get",
            "--query-file",
            qf_file,
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        with runner.isolated_filesystem():
            with open(qf_file, "w") as f:
                f.write(qf_contents)

            result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

    def test_json(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [
            cmd,
            "get",
            "--query",
            "(adapters > size(0))",
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

    def test_csv(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        if cmd == "devices":
            args1 = [
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
            args1 = [
                cmd,
                "get",
                "--query",
                "(adapters > size(0))",
                "--export-format",
                "csv",
                "--max-rows",
                "1",
            ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        csv_cols1 = ["internal_axon_id"]
        utils.check_csv_cols(stdout1, csv_cols1)

    def test_csv_delim(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        args1 = [
            cmd,
            "get",
            "--query",
            "(adapters > size(2))",
            "--export-format",
            "csv",
            "--max-rows",
            "1",
            "--export-delim",
            ",",
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        csv_cols1 = ["internal_axon_id"]
        rows = utils.check_csv_cols(stdout1, csv_cols1)
        row1 = rows[0]
        row1_adapters = row1["adapters"]
        assert len(row1_adapters.splitlines()) == 1
        assert len(row1_adapters.split(",")) > 2

    def test_csv_complex(self, request, monkeypatch, cmd):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)
        args1 = [
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

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        csv_cols1 = ["internal_axon_id"]
        utils.check_csv_cols(stdout1, csv_cols1)


class TestCmdGetBySubnet(object):
    """Pass."""

    def test_json(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [
            "devices",
            "get-by-subnet",
            "--value",
            "10.0.0.0/8",
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

    def test_csv(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [
            "devices",
            "get-by-subnet",
            "--value",
            "10.0.0.0/8",
            "--export-format",
            "csv",
            "--max-rows",
            "1",
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        csv_cols1 = ["internal_axon_id"]
        utils.check_csv_cols(stdout1, csv_cols1)


@pytest.mark.parametrize("get_by", ["get-by-hostname", "get-by-ip", "get-by-mac"])
class TestCmdGetByDevices(object):
    """Pass."""

    def test_json(self, request, monkeypatch, get_by):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [
            "devices",
            get_by,
            "--value",
            "RE:.*",
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

    def test_csv(self, request, monkeypatch, get_by):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [
            "devices",
            get_by,
            "--value",
            "RE:.*",
            "--export-format",
            "csv",
            "--max-rows",
            "1",
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        csv_cols1 = ["internal_axon_id"]
        utils.check_csv_cols(stdout1, csv_cols1)


@pytest.mark.parametrize("get_by", ["get-by-mail", "get-by-username"])
class TestCmdGetByUsers(object):
    """Pass."""

    def test_json(self, request, monkeypatch, get_by):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [
            "users",
            get_by,
            "--value",
            "RE:.*",
            "--export-format",
            "json",
            "--max-rows",
            "1",
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

    def test_csv(self, request, monkeypatch, get_by):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = [
            "users",
            get_by,
            "--value",
            "RE:.*",
            "--export-format",
            "csv",
            "--max-rows",
            "1",
        ]

        result1 = runner.invoke(cli=cli.cli, args=args1)

        exit_code1 = result1.exit_code
        stdout1 = result1.stdout
        stderr1 = result1.stderr

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        csv_cols1 = ["internal_axon_id"]
        utils.check_csv_cols(stdout1, csv_cols1)
