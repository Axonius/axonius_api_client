#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base example for setting up the API client."""
import axonius_api_client as axonapi  # noqa: F401
import click
from axonius_api_client.cli.context import CONTEXT_SETTINGS
from axonius_api_client.cli.options import AUTH, INPUT_FILE, add_options
from axonius_api_client.connect import Connect
from axonius_api_client.tools import echo_error, json_reload


def j(obj, **kwargs):
    """JSON dump utility."""
    print(json_reload(obj, **kwargs))


OP_MAPS = ["=", ">=", ">", "<", "<="]


class CustomConnect(Connect):
    """Pass."""

    def parse_checks(self, checks):
        """Pass."""
        ret = []
        for check in checks:
            name, version = check
            name = name.strip().lower()
            version = version.strip().lower()

            if not name:
                echo_error(f"Must supply agent name in {check}")

            op = "="
            for k in OP_MAPS:
                if version.startswith(k):
                    op = k
                    version = version.lstrip(k).strip()

            ret.append({"name": name, "version": version, "op": op})
        return ret


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
    "username",
    "display_name",
    "mail",
    "domain",
    "first_name",
    "last_name",
]


@click.command(context_settings=CONTEXT_SETTINGS)
@add_options(AUTH)
@click.option(
    "--column-first-name",
    "column_first_name",
    help="Name of column in CSV that has users first name",
    default="First Name",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--column-last-name",
    "column_last_name",
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
    "--column-first-name",
    "column_first_name",
    help="Name of column in CSV that has users first name",
    default="First Name",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--column-user-name",
    "column_user_name",
    help="Name of column in CSV that has users login name",
    default="SSO",
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
@INPUT_FILE
@click.pass_context
def cli(ctx, url, key, secret, input_file, checks, **kwargs):
    """Pass."""
    client = CustomConnect(url=url, key=key, secret=secret, certwarn=False)
    client.start()
    checks = client.parse_checks(checks)
    j(checks)


if __name__ == "__main__":
    cli()


"""
REQUIREDS
--input-file blah.csv
--check-agent "Name" "version" --check-agent "name" "" --....
--check-agent "carbonblack" "=2.3.4"
--check-agent "carbonblack" ">=2.3.4"


OPTIONALS
--column-first_name "First Name"
--column-last-name "Last Name"
--column-email "Email Address"
--column-user-name "SSO"
--user-fields ass dvcs, user name, display name, mail, domain, first name, last name
--device-fields hostname, asset name, agent versions, os.full_os_string

"""
"""
take in a csv
csv has columns: email, first name, last name
search for email in users
if not hits, search for first and last name
if no hits, diaf
if hit: find associated devices
if no associated devices, include in output csv that we don't know what the associated
output columns:
    users: ass dvcs, user name, display name, mail, domain, first name, last name
    devices: hostname, asset name, agent versions, MISSING AGENT VERSION, os.full_os_string
"""
