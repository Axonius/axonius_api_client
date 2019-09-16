# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

from axonius_api_client import cli, tools  # , exceptions

from .. import utils

# import pytest


class TestGrpCnx(object):
    """Pass."""

    def test_get_json(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

        args2 = ["adapters", "cnx", "get", "--rows", "-", "--export-format", "json"]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=stdout1)

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.LIST)

    def test_get_csv(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

        args2 = ["adapters", "cnx", "get", "--rows", "-", "--export-format", "csv"]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=stdout1)

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        csv_cols2 = ["adapter_name", "node_name", "id", "uuid", "status_raw", "error"]
        utils.check_csv_cols(stdout2, csv_cols2)

    def test_get_csv_settings(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

        args2 = [
            "adapters",
            "cnx",
            "get",
            "--rows",
            "-",
            "--export-format",
            "csv",
            "--include-settings",
        ]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=result1.stdout)

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        csv_cols2 = [
            "adapter_name",
            "node_name",
            "id",
            "uuid",
            "status_raw",
            "error",
            "settings",
        ]
        utils.check_csv_cols(stdout2, csv_cols2)

    def test_non_adapters_json(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        content = [{"x": "a"}]

        args1 = ["adapters", "cnx", "get", "--rows", "-"]
        result1 = runner.invoke(cli=cli.cli, args=args1, input=tools.json_dump(content))

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert not stdout1
        assert stderr1
        assert exit_code1 != 0

        errlines1 = stderr1.splitlines()

        exp = "** ERROR: No 'cnx' key found in adapter with keys: {}".format(
            list(content[0])
        )
        assert errlines1[-1] == exp

    def test_add_check_discover_delete_csv(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        csv_file = "badwolf.csv"
        csv_contents = "id,hostname\nbadwolf9131,badwolf\n"

        with runner.isolated_filesystem():
            with open(csv_file, "w") as f:
                f.write(csv_contents)

            args1 = [
                "adapters",
                "cnx",
                "add",
                "--adapter",
                "csv",
                "--config",
                "user_id={}".format(csv_file),
                "--config",
                "csv={}".format(csv_file),
                "--no-prompt-opt",
            ]
            result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, dict)

        args2 = ["adapters", "cnx", "check", "--rows", "-", "--no-error"]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=stdout1)

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.LIST)

        args3 = ["adapters", "cnx", "discover", "--rows", "-", "--no-error"]
        result3 = runner.invoke(cli=cli.cli, args=args3, input=stdout2)

        stderr3 = result3.stderr
        stdout3 = result3.stdout
        exit_code3 = result3.exit_code

        assert stdout3
        assert stderr3
        assert exit_code3 == 0

        json3 = tools.json_load(stdout3)
        assert isinstance(json3, tools.LIST)

        args4 = ["adapters", "cnx", "delete", "--rows", "-", "--force", "--wait", "0"]
        result4 = runner.invoke(cli=cli.cli, args=args4, input=stdout3)

        stderr4 = result4.stderr
        stdout4 = result4.stdout
        exit_code4 = result4.exit_code

        assert stdout4
        assert stderr4
        assert exit_code4 == 0

        json4 = tools.json_load(stdout4)
        assert isinstance(json4, tools.LIST)

    def test_add_delete_ad_config_args(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        csv_file = "badwolf.csv"
        csv_contents = "id,hostname\nbadwolf9131,badwolf\n"

        #
        configs = {
            "dc_name": "badwolf",
            "user": "badwolf",
            "password": "badwolf",
            "dns_server_address": "badwolf",
            "alternative_dns_suffix": "badwolf",
            "use_ssl": "Unencrypted",
            "ca_file": csv_file,
            "cert_file": csv_file,
            "private_key": csv_file,
            "fetch_disabled_devices": "y",
            "fetch_disabled_users": "y",
            "is_ad_gc": "y",
            "ldap_ou_whitelist": "badwolf1,badwolf2",
        }

        with runner.isolated_filesystem():
            with open(csv_file, "w") as f:
                f.write(csv_contents)

            args1 = [
                "adapters",
                "cnx",
                "add",
                "--adapter",
                "active_directory",
                "--no-error",
            ]
            for k, v in configs.items():
                args1.append("--config")
                args1.append("{}={}".format(k, v))

            result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, dict)

        args2 = ["adapters", "cnx", "delete", "--rows", "-", "--force", "--wait", "0"]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=stdout1)

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.LIST)

    def test_add_delete_ad_config_prompt_skips(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        csv_file = "badwolf.csv"
        csv_contents = "id,hostname\nbadwolf9131,badwolf\n"

        #
        skips = ["ca_file", "cert_file", "private_key"]

        configs = [
            "badwolf",  # dc_name
            "badwolf",  # user
            "badwolf",  # password
            "badwolf",  # dns_server_address
            "badwolf",  # alternative_dns_suffix
            "Unencrypted",  # use_ssl
            # csv_file,  # ca_file
            # csv_file,  # cert_file
            # csv_file,  # private_key
            "y",  # fetch_disabled_devices
            "y",  # fetch_disabled_users
            "y",  # is_ad_gc
            "badwolf1,badwolf2",  # ldap_ou_whitelist
        ]

        with runner.isolated_filesystem():
            with open(csv_file, "w") as f:
                f.write(csv_contents)

            args1 = [
                "adapters",
                "cnx",
                "add",
                "--adapter",
                "active_directory",
                "--no-error",
            ]
            for s in skips:
                args1 += ["--skip", s]

            result1 = runner.invoke(cli=cli.cli, args=args1, input="\n".join(configs))

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json_start_idx = stdout1.index("{")
        stdout1_stripped = stdout1[json_start_idx:]

        json1 = tools.json_load(stdout1_stripped)
        assert isinstance(json1, dict)

        args2 = ["adapters", "cnx", "delete", "--rows", "-", "--force", "--wait", "0"]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=stdout1_stripped)

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.LIST)

    def test_check_csv(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = ["adapters", "get", "-n", "active_directory"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

        args2 = ["adapters", "cnx", "get", "-r", "-", "-xt", "json"]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=stdout1)

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.LIST)

        runner = utils.load_clirunner(request, monkeypatch)

        args3 = ["adapters", "cnx", "check", "-r", "-", "-ne", "-xt", "csv"]
        result3 = runner.invoke(cli=cli.cli, args=args3, input=stdout2)

        stderr3 = result3.stderr
        stdout3 = result3.stdout
        exit_code3 = result3.exit_code

        assert stdout3
        assert stderr3
        assert exit_code3 == 0

        csv_cols3 = ["adapter_name", "node_name", "id", "uuid", "status_raw", "error"]
        utils.check_csv_cols(stdout3, csv_cols3)
