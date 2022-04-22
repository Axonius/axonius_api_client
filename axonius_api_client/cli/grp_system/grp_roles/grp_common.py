# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....constants.api import TABLE_FORMAT
from ....parsers.tables import tablize_roles
from ....tools import json_dump, listify
from ...context import SplitEquals, click
from ...options import TABLE_FMT


def getstr_grants(perms):
    """Pass."""
    grants = []

    for category, actions in perms.items():
        if all([v is True for k, v in actions.items()]):
            allows = "all"
        elif all([v is False for k, v in actions.items()]):
            allows = "none"
        else:
            allows = [k for k, v in actions.items() if v]
            allows = ",".join(allows)
        grants.append(f"{category}={allows!r}")

    return grants


def export_str_args(data, **kwargs):
    """Pass."""

    def getstr(obj):
        name = obj["name"]
        perms = obj["permissions_flat"]
        dsr = obj.get("data_scope_restriction")
        dsr_name = obj.get("data_scope_name")

        dsr_enabled = dsr.get("enabled", False)
        dsr_uuid = dsr.get("data_scope")
        dsr_show = dsr_name or dsr_uuid

        items = [
            f"--name {name!r}",
        ]
        items += [f"--perm {x}" for x in getstr_grants(perms)]
        if dsr_enabled and dsr_show:
            items.append(f"--data-scope {dsr_show!r}")

        return " ".join(items)

    return "\n".join(getstr(x) for x in listify(data))


def export_str(data, **kwargs):
    """Pass."""

    def getstr(obj):
        name = obj["name"]
        uuid = obj["uuid"]
        perms = obj["permissions_flat"]
        dsr = obj.get("data_scope_restriction")
        dsr_name = obj.get("data_scope_name")

        dsr_enabled = dsr.get("enabled", False)
        dsr_uuid = dsr.get("data_scope")
        dsr_show = dsr_name or dsr_uuid
        items = [
            "-----------------------------------------------",
            f"Name: {name}",
            f"UUID: {uuid}",
            f"Data Scope Enabled: {dsr_enabled}",
            f"Data Scope: {dsr_show!r}",
        ]
        items += [f"Permission Category {x}" for x in getstr_grants(perms)]

        return "\n".join(items)

    return "\n".join(getstr(x) for x in listify(data))


def export_table(data, table_format=TABLE_FORMAT, **kwargs):
    """Pass."""
    return tablize_roles(roles=listify(data), err="", fmt=table_format)


def export_json(data, **kwargs):
    """Pass."""
    return json_dump(data)


EXPORT_FORMATS: dict = {
    "json": export_json,
    "str": export_str,
    "str-args": export_str_args,
    "table": export_table,
}

OPT_EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(list(EXPORT_FORMATS)),
    help="Format to export data in",
    default="table",
    show_envvar=True,
    show_default=True,
)

OPT_ROLE_NAME = click.option(
    "--name",
    "-n",
    "name",
    help="Name of role",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_PERMS = click.option(
    "--perm",
    "-p",
    "perms",
    help=(
        "Permissions like $CATEGORY=$ACTION1,$ACTION2,... Can use $CATEGORY_NAME=all or "
        "$CATEGORY_NAME=none (MULTIPLE)"
    ),
    required=True,
    show_envvar=True,
    show_default=True,
    type=SplitEquals(),
    multiple=True,
)


OPT_DATA_SCOPE = click.option(
    "--data-scope",
    "-ds",
    "data_scope",
    help="Name or UUID of Data Scope restriction to apply",
    required=False,
    show_envvar=True,
    show_default=True,
)

OPTS_EXPORT = [OPT_EXPORT, TABLE_FMT]
