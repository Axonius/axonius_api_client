#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base example for setting up the API client."""
import codecs
import copy
import csv
import io

import click
from packaging import version as pkg_version

import axonius_api_client as axonapi  # noqa: F401
from axonius_api_client.cli.context import CONTEXT_SETTINGS
from axonius_api_client.cli.options import AUTH, add_options
from axonius_api_client.connect import Connect
from axonius_api_client.tools import (
    bom_strip,
    echo_error,
    echo_ok,
    echo_warn,
    get_path,
    json_reload,
    listify,
    path_read,
)


def j(obj, **kwargs):
    """JSON dump utility."""
    print(json_reload(obj, **kwargs))


ASS_DVC = "agg:associated_devices.device_caption"
USERNAME = "agg:username"
DISPLAY_NAME = "agg:display_name"
MAIL = "agg:mail"
DOMAIN = "agg:domain"
FIRST_NAME = "agg:first_name"
LAST_NAME = "agg:last_name"
HOSTNAME = "agg:hostname"
NAME = "agg:name"
AGENT_VERS = "agg:agent_versions"
OS_STR = "agg:os.os_str"
LAST_USED_USERS = "agg:last_used_users"
IPS = "agg:network_interfaces.ips"
AXID = "internal_axon_id"

FIELDS_USER = [
    ASS_DVC,
    USERNAME,
]

FIELDS_DEVICE = [
    NAME,
    HOSTNAME,
    AGENT_VERS,
    OS_STR,
    IPS,
]

COL_USERNAME = "SSO"

COL_USERLINK = "Axonius User Link"
COL_DVCLINK = "Axonius Device Link"
COL_DVCNAME = "Axonius Device Name"
COL_DVCHOSTNAME = "Axonius Device Host Name"
COL_DVCIP = "Axonius Device IP"
COL_DVCOS = "Axonius Device OS"
COL_DVCAGENTS = "Axonius Device Agents"
COLS_OUTPUT = [
    COL_USERLINK,
    COL_DVCLINK,
    COL_DVCNAME,
    COL_DVCHOSTNAME,
    COL_DVCIP,
    COL_DVCOS,
    COL_DVCAGENTS,
]
COL_CHECKNAME = "Name"
COL_CHECKVER = "Version"
COL_CHECKSTAT = "Status"
COLS_CHECK = [
    COL_CHECKNAME,
    COL_CHECKVER,
    COL_CHECKSTAT,
]
VER_OPS = ["equals", "greaterthan", "lessthan"]


class CustomConnect(Connect):
    """Pass."""

    def run(self, users_csv, checks_csv, col_username, output_file, **kwargs):
        """Pass."""
        self.kwargs = kwargs
        self.col_username = col_username
        user_columns, user_rows = self._read_csv(path=users_csv, required=[col_username])

        _, check_rows = self._read_csv(path=checks_csv, required=COLS_CHECK)
        checks = self._parse_checks(rows=check_rows)
        rows = self.get_output_rows(user_rows=user_rows, checks=checks)
        columns = user_columns + COLS_OUTPUT + [x["col"] for x in checks]
        self.write_output(path=output_file, rows=rows, columns=columns)

    def write_output(self, path, rows, columns):
        """Pass."""
        path = get_path(obj=path)
        stream = path.open("w")
        stream.write(codecs.BOM_UTF8.decode("utf-8"))
        writer = csv.DictWriter(
            stream,
            fieldnames=columns,
            lineterminator="\n",
        )
        writer.writerow(dict(zip(columns, columns)))
        writer.writerows(rows)
        stream.close()
        self.spew_info(f"Wrote output to {path}")

    def get_output_rows(self, user_rows, checks):
        """Pass."""
        output_rows = []

        for idx, user_row in enumerate(user_rows):
            username = (user_row.get(self.col_username) or "").strip()
            user = self.find_user(user_row=user_row, idx=idx, username=username)
            output_rows += self.do_checks(user_row=user_row, user=user, checks=checks)
        return output_rows

    def get_axon_link(self, asset, type):
        """Pass."""
        return f"{self.HTTP.url}/{type}/{asset[AXID]}" if asset else "NOT FOUND"

    def do_checks(self, user_row, user, checks):
        """Pass."""
        for check in checks:
            user_row[check["col"]] = False

        if not user:
            user_row[COL_DVCLINK] = "NO USER FOUND"
            return [user_row]

        dvcs = self.find_dvcs(user=user)

        if not dvcs:
            user_row[COL_DVCLINK] = "NO ASSOCIATED DEVICES FOUND"
            return [user_row]

        user_dvc_rows = []
        for dvc in dvcs:
            agent_vers = dvc.get(AGENT_VERS)
            user_row_dvc = copy.deepcopy(user_row)
            user_dvc_rows.append(user_row_dvc)
            user_row_dvc[COL_DVCLINK] = self.get_axon_link(asset=dvc, type="devices")
            user_row_dvc[COL_DVCNAME] = "\n".join(listify(dvc.get(NAME)))
            user_row_dvc[COL_DVCHOSTNAME] = "\n".join(listify(dvc.get(HOSTNAME)))
            user_row_dvc[COL_DVCIP] = "\n".join(listify(dvc.get(IPS)))
            user_row_dvc[COL_DVCOS] = "\n".join(listify(dvc.get(OS_STR)))
            user_row_dvc[COL_DVCAGENTS] = self.get_agent_vers(agent_vers=agent_vers)
            for check in checks:
                user_row_dvc[check["col"]] = self.do_check(agent_vers, check)
        return user_dvc_rows

    def do_check(self, agent_vers, check):
        """Pass."""
        check_name = check["name"]
        check_status = check["status"]
        check_version = check["version"]
        check_version_op = check.get("version_op", "greaterthan")

        for agent_ver in agent_vers:
            agent_name = agent_ver.get("adapter_name") or ""
            agent_status = agent_ver.get("agent_status") or ""
            agent_version = agent_ver.get("agent_version") or ""
            if not check_name == agent_name:
                continue

            if check_status:
                if not check_status == agent_status:
                    continue

            if check_version:
                parsed_agent_version = pkg_version.parse(agent_version)
                parsed_check_version = pkg_version.parse(check_version)

                if check_version_op == "greaterthan":
                    if not parsed_agent_version >= parsed_check_version:
                        continue
                if check_version_op == "lessthan":
                    if not parsed_agent_version <= parsed_check_version:
                        continue
                if check_version_op == "equals":
                    if not agent_version == check_version:
                        continue
            return True

        return False

    def get_agent_vers(self, agent_vers):
        """Pass."""
        lines = []
        for agent_ver in listify(agent_vers):
            name = agent_ver.get("adapter_name") or ""
            status = agent_ver.get("agent_status") or ""
            version = agent_ver.get("agent_version") or ""
            lines.append(f"name: {name}, version: {version}, status: {status}")
        return "\n".join(lines)

    def find_dvcs(self, user):
        """Pass."""
        row_txt = user["row_txt"]
        dvcs = listify(user.get(ASS_DVC))
        found = []
        for dvc in dvcs:
            wiz_entries = self.dvc_wiz_entries(dvc=dvc)
            query = self.devices.wizard.parse(wiz_entries)["query"]
            self.spew_debug(f"Looking for devices searching for {dvc!r} using query {query}")
            dvcs = self.devices.get(
                query=query,
                field_null=True,
                fields_default=False,
                fields=FIELDS_DEVICE,
                field_compress=True,
            )
            self.spew_debug(f"Found {len(dvcs)} devices searching for {dvc!r} {row_txt}")
            found += dvcs
        self.spew_info(f"Found {len(found)} devices {row_txt}")
        return found

    def dvc_wiz_entries(self, dvc):
        """Pass."""
        entries = [
            {
                "value": f"hostname contains {dvc}",
                "type": "simple",
            },
            {"value": f"| name contains {dvc}", "type": "simple"},
            {"value": f"| id contains {dvc}", "type": "simple"},
        ]
        return entries

    def find_user(self, user_row, idx, username):
        """Pass."""
        row_txt = f"for username {username!r} in row {idx + 1}"

        if not username:
            self.spew_warn(f"Empty value {row_txt}")
            user_row[COL_USERLINK] = "Empty username"
            return

        found = [x for x in self.user_assets if username in listify(x.get(USERNAME))]

        if not found:
            self.spew_warn(f"No user found {row_txt}")
            user_row[COL_USERLINK] = "No user found"
            return

        if len(found) > 1:
            self.spew_warn(f"Found more than one user {row_txt}")
            user_row[COL_USERLINK] = f"More than one matching user found ({len(found)})"
            return

        user = found[0]
        user_row[COL_USERLINK] = self.get_axon_link(asset=user, type="users")
        user["row"] = user_row
        user["row_username"] = username
        user["row_idx"] = idx
        user["row_txt"] = row_txt
        return user

    def _parse_checks(self, rows):
        """Pass."""
        checks = []

        for idx, row in enumerate(rows):
            name = (row.get("Name") or "").strip()
            version = (row.get("Version") or "").strip()
            status = (row.get("Status") or "").strip()
            version_op = (row.get("Version Operator") or "greaterthan").strip()
            version_op = version_op.lower().strip().replace(" ", "_")

            col_lines = ["Agent Check", f"Name: {name}"]
            if version:
                col_lines.append(f"Version: {version}")
            if status:
                col_lines.append(f"Status: {status}")
            if version_op:
                col_lines.append(f"Version Operator: {version_op}")

            col = "\n".join(col_lines)
            rtxt = (
                f"for row {idx + 1} with name {name!r}, version {version!r}, status {status!r}, "
                f"version operator: {version_op!r}"
            )

            if version_op not in VER_OPS:
                self.spew_error(f"Invalid version operator, must be one of {VER_OPS} {rtxt}")

            if not name:
                self.spew_error(f"Must supply agent name {rtxt}")

            if name not in self.agent_names:
                valids = "\n - " + "\n - ".join(self.agent_names)
                self.spew_error(f"Invalid agent name {rtxt}, valids:{valids}")

            self.spew_debug(f"Add check {rtxt}")
            checks.append(
                {
                    "name": name,
                    "version": version,
                    "status": status,
                    "col": col,
                    "version_op": version_op,
                }
            )
        return checks

    def _read_csv(self, path, required):
        """Pass."""
        path, content = path_read(obj=path)
        content = bom_strip(content=content)
        reader = csv.DictReader(io.StringIO(content))

        rows = [x for x in reader]
        if not rows:
            self.spew_error("No rows supplied in CSV!")

        columns = listify(reader.fieldnames)
        self.spew_debug(f"CSV file {path} has columns {columns}")
        missing = [x for x in required if x not in columns]
        if missing:
            missing = ", ".join(missing)
            self.spew_error(f"Missing required columns {missing} in CSV file {path}")

        return columns, rows

    @property
    def user_assets(self):
        """Pass."""
        if not hasattr(self, "_user_assets"):
            self._user_assets = self.users.get(
                fields=FIELDS_USER, fields_default=False, field_compress=True, field_null=True
            )
            self.spew_info(f"Fetched {len(self._user_assets)} users")
        return self._user_assets

    @property
    def agent_names(self):
        """Pass."""
        if not hasattr(self, "_agent_names"):
            self._agent_names = self.devices.fields.get_field_name(
                value="agg:agent_versions.adapter_name", key=None
            )["enum"]
        return self._agent_names

    def spew_info(self, msg, fg="green", bold=True):
        """Pass."""
        echo_ok(msg, fg=fg, bold=bold)

    def spew_debug(self, msg):
        """Pass."""
        if self.kwargs.get("verbose", False):
            echo_ok(msg, fg="blue", bold=False)

    def spew_warn(self, msg):
        """Pass."""
        echo_warn(msg)

    def spew_error(self, msg):
        """Pass."""
        echo_error(msg)


@click.command(context_settings=CONTEXT_SETTINGS)
@add_options(AUTH)
@click.option(
    "--column-username",
    "col_username",
    help="Name of column in CSV that has user name",
    default=COL_USERNAME,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--verbose/--no-verbose",
    "-v/-nv",
    "verbose",
    default=False,
    help="Be noisy.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--users-csv",
    "-uc",
    "users_csv",
    help="File to read usernames from",
    required=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--checks-csv",
    "-cc",
    "checks_csv",
    help="File to read agent checks from",
    required=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--output-file",
    "-of",
    "output_file",
    help="File to write output to",
    required=True,
    show_envvar=True,
    show_default=True,
)
@click.pass_context
def cli(ctx, url, key, secret, **kwargs):
    """Pass."""
    client = CustomConnect(url=url, key=key, secret=secret, certwarn=False)
    client.start()
    client.run(**kwargs)


if __name__ == "__main__":
    cli()
