# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click
import pytest

from axonius_api_client import cli, tools  # , exceptions

from .. import utils


def badwolf_cb(x, **kwargs):
    """Pass."""
    return ["a", "b"]


class TestGrpCnx(object):
    """Pass."""

    @pytest.mark.parametrize(
        "schema,ptype",
        [
            [{"type": "string", "enum": ["x", "a"]}, click.Choice],
            [{"type": "badwolf"}, type(None)],
            [{"type": "bool"}, click.BOOL.__class__],
        ],
    )
    def test_determine_type(self, schema, ptype):
        """Pass."""
        ret = cli.grp_cnx.grp_common.determine_type(schema)
        assert isinstance(ret, ptype), "{!r} {!r}".format(schema, ptype)

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

    def test_get_cnx_by_uuid(self, request, monkeypatch):
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
        cnxs = [x["cnx"] for x in json1 if x["cnx"]]
        cnx1_id = cnxs[0][0]["uuid"]

        args2 = ["adapters", "cnx", "get", "--rows", "-", "--uuid", cnx1_id]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=stdout1)
        del stdout1

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.LIST)
        assert json2[0]["uuid"] == cnx1_id
        assert len(json2) == 1

    def test_get_cnx_by_id(self, request, monkeypatch):
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
        cnxs = [x["cnx"] for x in json1 if x["cnx"]]
        cnx1_id = cnxs[0][0]["id"]

        args2 = ["adapters", "cnx", "get", "--rows", "-", "--id", cnx1_id]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=stdout1)
        del stdout1

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 0

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.LIST)
        assert json2[0]["id"] == cnx1_id
        assert len(json2) == 1

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

        exp = "  Item must have keys:"
        assert errlines1[-2].startswith(exp)

    def test_add_show_config_json(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = ["adapters", "cnx", "add", "--adapter", "csv", "--show-config", "json"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)
        for x in json1:
            assert isinstance(x, dict)

    def test_add_show_config_text(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = ["adapters", "cnx", "add", "--adapter", "csv", "--show-config", "text"]
        result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 0

    def test_add_check_discover_delete_csv(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        csv_file = "badwolf.csv"
        csv_contents = "id,hostname\nbadwolf9131,badwolf\n"
        """
echo "x" > /tmp/input.csv
axonshell a c a -a csv -c user_id=input.csv -c csv=/tmp/input.csv -npo | \
axonshell a c c -r - -ne | \
axonshell a c di -r - -ne | \
axonshell a c de -r - -f -w 0
        """
        with runner.isolated_filesystem():
            with open(csv_file, "w") as f:
                f.write(csv_contents)

            csv_path = tools.path(csv_file)
            args1 = [
                "adapters",
                "cnx",
                "add",
                "--adapter",
                "csv",
                "--config",
                "user_id={}".format(csv_file),
                "--config",
                "is_users_csv=False",
                "--config",
                "is_installed_sw=False",
                "--config",
                "csv={}".format(csv_path),
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

        args2 = ["adapters", "cnx", "check", "--rows", "-"]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=stdout1)

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 1

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.LIST)

        args3 = ["adapters", "cnx", "discover", "--rows", "-"]
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

    def test_add_check_discover_delete_csv_err(self, request, monkeypatch):
        """Pass."""
        runner = utils.load_clirunner(request, monkeypatch)

        csv_file = "badwolf.csv"
        csv_contents = "xx,yy\nbadwolf9131,badwolf\n"
        """
echo "x" > /tmp/input.csv
axonshell a c a -a csv -c user_id=input.csv -c csv=/tmp/input.csv -npo | \
axonshell a c c -r - -ne | \
axonshell a c di -r - -ne | \
axonshell a c de -r - -f -w 0
        """
        with runner.isolated_filesystem():
            with open(csv_file, "w") as f:
                f.write(csv_contents)

            csv_path = tools.path(csv_file)
            args1 = [
                "adapters",
                "cnx",
                "add",
                "--adapter",
                "csv",
                "--config",
                "user_id={}".format(csv_file),
                "--config",
                "is_users_csv=False",
                "--config",
                "is_installed_sw=False",
                "--config",
                "csv={}".format(csv_path),
                "--no-prompt-opt",
            ]
            result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 1

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, dict)

        args2 = ["adapters", "cnx", "check", "--rows", "-"]
        result2 = runner.invoke(cli=cli.cli, args=args2, input=stdout1)

        stderr2 = result2.stderr
        stdout2 = result2.stdout
        exit_code2 = result2.exit_code

        assert stdout2
        assert stderr2
        assert exit_code2 == 1

        json2 = tools.json_load(stdout2)
        assert isinstance(json2, tools.LIST)

        args3 = ["adapters", "cnx", "discover", "--rows", "-"]
        result3 = runner.invoke(cli=cli.cli, args=args3, input=stdout2)

        stderr3 = result3.stderr
        stdout3 = result3.stdout
        exit_code3 = result3.exit_code

        assert stdout3
        assert stderr3
        assert exit_code3 == 1

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

    def test_delete_error(self, request, monkeypatch):
        """Pass."""
        delete_me = {
            "adapter_name": "badwolf",
            "adapter_name_raw": "badwolf",
            "config_raw": {},
            "node_id": "badwolf",
            "node_name": "badwolf",
            "id": "badwolf",
            "uuid": "badwolf",
            "status": "badwolf",
            "error": "badwolf",
        }
        runner = utils.load_clirunner(request, monkeypatch)

        args1 = ["adapters", "cnx", "delete", "--rows", "-", "--force", "--wait", "0"]
        result1 = runner.invoke(
            cli=cli.cli, args=args1, input=tools.json_dump(delete_me)
        )
        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 1

        json1 = tools.json_load(stdout1)
        assert isinstance(json1, tools.LIST)

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
            "is_ad_gc": "y",
            "ldap_ou_whitelist": "badwolf1,badwolf2",
            "do_not_fetch_users": "false",
            "fetch_disabled_devices": "true",
            "fetch_disabled_users": "true",
        }

        with runner.isolated_filesystem():
            with open(csv_file, "w") as f:
                f.write(csv_contents)

            args1 = ["adapters", "cnx", "add", "--adapter", "active_directory"]
            for k, v in configs.items():
                args1.append("--config")
                args1.append("{}={}".format(k, v))

            result1 = runner.invoke(cli=cli.cli, args=args1)

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 1

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

        skips = ["ca_file", "cert_file", "private_key"]

        """
        dc_name
        user
        password
        do_not_fetch_users
        fetch_disabled_devices
        fetch_disabled_users
        dns_server_address
        alternative_dns_suffix
        use_ssl
        ca_file
        is_ad_gc
        ldap_ou_whitelist
        """
        configs = [
            "badwolf",  # dc_name
            "badwolf",  # user
            "badwolf",  # password
            "n",  # do_not_fetch_users
            "y",  # fetch_disabled_devices
            "y",  # fetch_disabled_users
            "badwolf",  # dns_server_address
            "badwolf",  # alternative_dns_suffix
            "Unencrypted",  # use_ssl
            "y",  # is_ad_gc
            "badwolf1,badwolf2",  # ldap_ou_whitelist
        ]

        args1 = ["adapters", "cnx", "add", "--adapter", "active_directory"]
        for s in skips:
            args1 += ["--skip", s]

        result1 = runner.invoke(cli=cli.cli, args=args1, input="\n".join(configs))

        stderr1 = result1.stderr
        stdout1 = result1.stdout
        exit_code1 = result1.exit_code

        assert stdout1
        assert stderr1
        assert exit_code1 == 1

        json_start_idx = stdout1.index("{")
        stdout1_stripped = stdout1[json_start_idx:]

        json1 = tools.json_load(stdout1_stripped)
        assert isinstance(json1, dict)

        args2 = [
            "adapters",
            "cnx",
            "delete",
            "--rows",
            "-",
            "--force",
            "--wait",
            "0",
            "--no-error",
        ]
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
        exit_code1 = result1.exit_code

        assert result1.stdout
        assert stderr1
        assert exit_code1 == 0

        assert isinstance(tools.json_load(result1.stdout), tools.LIST)

        args3 = ["-nw", "adapters", "cnx", "check", "-r", "-", "-ne", "-xt", "csv"]
        result3 = runner.invoke(cli=cli.cli, args=args3, input=result1.stdout)

        stderr3 = result3.stderr
        stdout3 = result3.stdout
        # exit_code3 = result3.exit_code

        assert stdout3
        assert stderr3

        csv_cols3 = ["adapter_name", "node_name", "id", "uuid", "status_raw", "error"]
        utils.check_csv_cols(stdout3, csv_cols3)


class TestCheckEmpty(object):
    """Pass."""

    @pytest.mark.parametrize("value", tools.EMPTY, scope="class")
    def test_empty_value(self, value):
        """Pass."""
        ctx = utils.get_mockctx()

        cli.grp_cnx.grp_common.check_empty(
            ctx=ctx,
            this_data=[],
            prev_data=[],
            value_type="badwolf",
            value=value,
            objtype="wolves",
            known_cb=None,
            known_cb_key="bad",
        )

    def test_empty_data(self, capsys):
        """Pass."""
        ctx = utils.get_mockctx()

        with pytest.raises(SystemExit):
            cli.grp_cnx.grp_common.check_empty(
                ctx=ctx,
                this_data=[],
                prev_data=[{"a": "1", "b": "2"}],
                value_type="badwolf",
                value=["d", "e"],
                objtype="wolves",
                known_cb=badwolf_cb,
                known_cb_key="x",
            )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 5

        stdout = captured.out.splitlines()
        assert not stdout

        assert stderr[0] == "** ERROR: Valid wolves:"
        assert stderr[1] == "  a"
        assert stderr[2] == "  b"
        assert stderr[3] == ""
        assert stderr[4] == "** ERROR: No wolves found when searching by badwolf: d, e"

    def test_not_empty(self, capsys):
        """Pass."""
        ctx = utils.get_mockctx()

        cli.grp_cnx.grp_common.check_empty(
            ctx=ctx,
            this_data=[{"a": "1"}],
            prev_data=[{"a": "1", "b": "2"}],
            value_type="badwolf",
            value=["a"],
            objtype="wolves",
            known_cb=badwolf_cb,
            known_cb_key="x",
        )

        captured = capsys.readouterr()

        stderr = captured.err.splitlines()
        assert len(stderr) == 1

        stdout = captured.out.splitlines()
        assert not stdout

        assert stderr[0] == "** Found 1 wolves by badwolf: a"
