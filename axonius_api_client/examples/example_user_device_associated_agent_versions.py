#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base example for setting up the API client."""
import csv
import io

import click

import axonius_api_client as axonapi  # noqa: F401
from axonius_api_client.cli.context import CONTEXT_SETTINGS
from axonius_api_client.cli.options import AUTH, INPUT_FILE, add_options
from axonius_api_client.connect import Connect
from axonius_api_client.tools import (
    bom_strip,
    echo_error,
    echo_ok,
    echo_warn,
    json_reload,
    listify,
    read_stream,
    strip_left,
)


def j(obj, **kwargs):
    """JSON dump utility."""
    print(json_reload(obj, **kwargs))


ASS_DVC_FIELD = "specific_data.data.associated_devices"
USERNAME_FIELD = "specific_data.data.username"
DEVICE_FIELDS = [
    "hostname",
    "name",
    "agent_versions",
    "os.os_str",
    "last_used_users",
    "network_interfaces.ips",
]

USER_FIELDS = [
    "associated_devices",
    # "username",
    # "display_name",
    # "mail",
    # "domain",
    # "first_name",
    # "last_name",
]

OP_MAPS = [
    ">=",
    "<=",
    "=",
    ">",
    "<",
]


def echo_debug(msg, fg="blue", bold=False, **kwargs):
    """Pass."""
    if kwargs["verbose"]:
        echo_ok(msg, fg=fg, bold=bold)


class CustomConnect(Connect):
    """Pass."""

    def read_csv(self, input_file, **kwargs):
        """Pass."""
        looking_for = self.get_looking_for(**kwargs)

        content = read_stream(stream=input_file)
        content = bom_strip(content=content)
        reader = csv.DictReader(io.StringIO(content))

        rows = [x for x in reader]
        if not rows:
            echo_error("No rows supplied in CSV!")

        columns = listify(reader.fieldnames)
        echo_debug(f"found columns {columns}", **kwargs)
        missing = [x for x in looking_for.values() if x not in columns]
        if missing:
            errs = [
                f"Missing required columns {missing}",
                f"all required columns {looking_for}",
                f"found columns {columns}",
            ]
            echo_error("\n  ".join(errs))

        return rows

    def get_looking_for(self, **kwargs):
        """Pass."""
        return {k: v for k, v in kwargs.items() if k.startswith("column_")}

    def find_users(self, rows, **kwargs):
        """Pass."""
        for idx, row in enumerate(rows):
            row["log"] = []
            found = {
                "firstlast": self.get_by_firstlast(row=row, idx=idx, **kwargs),
                "email": self.get_by_email(row=row, idx=idx, **kwargs),
                "username": self.get_by_username(row=row, idx=idx, **kwargs),
            }
            user = self.pick_user(found=found, row=row, idx=idx, **kwargs)

            ass_dvcs = listify(user.get(ASS_DVC_FIELD, []))
            username = listify(user.get(USERNAME_FIELD), [])

            if not ass_dvcs:
                msg = f"No associated devices found for {username}"
                print(msg)
                # print(f"NO associated devices found for user {username}")
                return

            print(user)

    def pick_user(self, found, row, **kwargs):
        """Pass."""
        pri_keys = ["pri_username", "pri_email", "pri_firstlast"]
        priorities = [[strip_left(k, "pri_"), kwargs[k]] for k in pri_keys]
        priorities = sorted(priorities, key=lambda x: x[1])

        idx = kwargs["idx"] + 1

        user = {}
        user_from = ""

        for key, pri in priorities:
            found_user = found[key]
            if user and found_user and user != found_user:
                msg = (
                    f"Different user found for {key}, but different than user found from "
                    f"{user_from}, will use user from {user_from}"
                )
                echo_warn(f"in row {idx + 1}, {msg}")
                row["log"].append(msg)
                break

            if found_user:
                user_from = key
                user = found_user
        return user

    def get_by_username(self, row, **kwargs):
        """Pass."""
        looking_for = self.get_looking_for(**kwargs)
        operator = kwargs["search_operator"]
        idx = kwargs["idx"] + 1

        col = looking_for["column_email"]
        value = row.get(col)
        info = f"{col}: {value!r}"

        if not value:
            msg = f"empty {info}"
            echo_debug(f"in row {idx}, {msg}", fg="yellow", **kwargs)
            row["log"].append(msg)
            return {}

        user_entries = [
            {"type": "simple", "value": f"mail {operator} {value}"},
        ]
        query = self.users.wizard.parse(entries=user_entries)["query"]
        return self.get_user(row=row, query=query, src="username", **kwargs)

    def get_by_email(self, row, **kwargs):
        """Pass."""
        looking_for = self.get_looking_for(**kwargs)
        operator = kwargs["search_operator"]
        idx = kwargs["idx"] + 1

        col = looking_for["column_username"]
        value = row.get(col)
        info = f"{col}: {value!r}"

        if not value:
            msg = f"empty {info}"
            echo_debug(f"in row {idx}, {msg}", fg="yellow", **kwargs)
            row["log"].append(msg)
            return {}

        user_entries = [
            {"type": "simple", "value": f"username {operator} {value}"},
        ]
        query = self.users.wizard.parse(entries=user_entries)["query"]
        return self.get_user(row=row, src="email", query=query, **kwargs)

    def get_by_firstlast(self, row, **kwargs):
        """Pass."""
        looking_for = self.get_looking_for(**kwargs)
        operator = kwargs["search_operator"]
        idx = kwargs["idx"] + 1

        first_col = looking_for["column_firstname"]
        last_col = looking_for["column_lastname"]
        first = row.get(first_col)
        last = row.get(last_col)
        info = f"{first_col}: {first!r} and {last_col}: {last!r}"

        if not all([first, last]):
            msg = f"empty {info}"
            echo_debug(f"in row {idx}, {msg}", fg="yellow", **kwargs)
            row["log"].append(msg)
            return {}

        user_entries = [
            {"type": "simple", "value": f"first_name {operator} {first}"},
            {"type": "simple", "value": f"last_name {operator} {last}"},
        ]
        query = self.users.wizard.parse(entries=user_entries)["query"]
        return self.get_user(row=row, query=query, src="firstlast", **kwargs)

    def get_user(self, row, query, src, **kwargs):
        """Pass."""
        idx = kwargs["idx"] + 1
        echo_debug(f"in row {idx}, Looking for user with query: {query}", fg="cyan", **kwargs)

        found = self.users.get(query=query, fields=USER_FIELDS, field_null=True)

        if not found:
            msg = f"Did not find user by {src} using query: {query}"
            echo_debug(f"in row {idx}, {msg}", **kwargs)
            row["log"].append(msg)
            return {}

        if len(found) > 1:
            msg = f"Found too many ({len(found)}) users by {src} using query: {query}"
            echo_ok(
                f"in row {idx}, {msg}",
                fg="yellow",
                bold=False,
            )
            row["log"].append(msg)
            return {}

        found = found[0]
        msg = f"Found user by {src} using query: {query}"
        echo_ok(f"in row {idx}, {msg}")
        row["log"].append(msg)

        return found

    def parse_checks(self, checks):
        """Pass."""
        ret = []
        for check in checks:
            name, version = check
            name = name.strip().lower()
            version = version.strip().lower()
            op = None

            if not name:
                echo_error(f"Must supply agent name in {check}")

            if version:
                split_version = version.split(" ")
                if not len(split_version) == 2:
                    echo_error(f"Must supply valid operator at beginning, one of {OP_MAPS}")

                op, version = split_version
                op = op.strip()
                version = version.strip()

                if op not in OP_MAPS:
                    echo_error(f"Invalid operator {op!r}, begin with one of {OP_MAPS}")

            ret.append({"name": name, "version": version, "op": op})
        return ret


@click.command(context_settings=CONTEXT_SETTINGS)
@add_options(AUTH)
@click.option(
    "--column-first-name",
    "column_firstname",
    help="Name of column in CSV that has users first name",
    default="First Name",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--column-last-name",
    "column_lastname",
    help="Name of column in CSV that has users last name",
    default="Last Name",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--column-email",
    "column_email",
    help="Name of column in CSV that has users email",
    default="Email Address",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--column-user-name",
    "column_username",
    help="Name of column in CSV that has users login name",
    default="SSO",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--search-operator",
    "search_operator",
    help="Operator to use when finding users",
    default="equals",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--pri-username",
    "pri_username",
    help="Priority for username result if found and different than firstlast or email",
    default=4,
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--pri-firstlast",
    "pri_firstlast",
    help="Priority for firstlast result if found and different than username or email",
    default=2,
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--pri-email",
    "pri_email",
    help="Priority for email result if found and different than firstlast or username",
    default=1,
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--check-agent",
    "-ca",
    "checks",
    help="Agent name and version to check for",
    multiple=True,
    nargs=2,
    show_envvar=True,
    show_default=True,
    required=True,
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
@INPUT_FILE
@click.pass_context
def cli(ctx, url, key, secret, checks, **kwargs):
    """Pass."""
    client = CustomConnect(url=url, key=key, secret=secret, certwarn=False)
    client.start()
    checks = client.parse_checks(checks)
    rows = client.read_csv(**kwargs)
    client.find_users(rows=rows, **kwargs)
    return rows


if __name__ == "__main__":
    cli()


"""

OPTIONALS
--column-first_name "First Name"
--column-last-name "Last Name"
--column-email "Email Address"
--column-user-name "SSO"

"""
"""
search for email in users
if not hits, search for first and last name
if no hits, diaf
if hit: find associated devices
if no associated devices, include in output csv that we don't know what the associated
output columns:
    users: ass dvcs, user name, display name, mail, domain, first name, last name
    devices: hostname, asset name, agent versions, MISSING AGENT VERSION, os.full_os_string
"""
