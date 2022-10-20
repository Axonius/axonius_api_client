# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup
from . import (
    cmd_count,
    cmd_count_by_saved_query,
    cmd_destroy,
    cmd_get,
    cmd_get_by_id,
    cmd_get_by_saved_query,
    cmd_get_fields,
    cmd_get_fields_default,
    cmd_get_tags,
    cmds_run_enforcement,
    grp_saved_query,
)
from .grp_common import (
    GET_BY_VALUE_BUILDERS,
    GET_BY_VALUE_FIELD,
    GET_BY_VALUE_REGEX_BUILDERS,
    GET_BY_VALUES_BUILDERS,
    gen_get_by_cmd,
)


@click.group(cls=AliasedGroup)
def devices():
    """Group: Work with device assets."""


@click.group(cls=AliasedGroup)
def users():
    """Group: Work with user assets."""


@click.group(cls=AliasedGroup)
def vulnerabilities():
    """Group (BETA!): Work with vulnerability assets."""


CMDS = [
    grp_saved_query.saved_query,
    cmd_count.cmd,
    cmd_count_by_saved_query.cmd,
    cmd_get_fields.cmd,
    cmd_get_fields_default.cmd,
    cmd_get.cmd,
    cmd_get_by_saved_query.cmd,
    cmd_get_tags.cmd,
    cmd_get_by_id.cmd,
    cmd_destroy.cmd,
    *cmds_run_enforcement.CMDS,
]

for cmd in CMDS:
    users.add_command(cmd)
    devices.add_command(cmd)
    vulnerabilities.add_command(cmd)


def add_cmd(grp_obj, method, cmd):
    """Pass."""
    grp_obj.add_command(cmd)
    globals()[f"cmd_{method}"] = cmd


def add_cmds(grp_obj, fields):
    """Pass."""
    for field in fields:
        method = f"get_by_{field}"
        cmd = gen_get_by_cmd(
            options=GET_BY_VALUE_BUILDERS,
            doc=f"Get assets where {field} equals value",
            cmd_name=method.replace("_", "-"),
            method=method,
        )
        add_cmd(grp_obj=grp_obj, method=method, cmd=cmd)

        method = f"get_by_{field}s"
        cmd = gen_get_by_cmd(
            options=GET_BY_VALUES_BUILDERS,
            doc=f"Get assets where {field} equals multiple values",
            cmd_name=method.replace("_", "-"),
            method=method,
        )
        add_cmd(grp_obj=grp_obj, method=method, cmd=cmd)

        method = f"get_by_{field}_regex"
        cmd = gen_get_by_cmd(
            options=GET_BY_VALUE_REGEX_BUILDERS,
            doc=f"Get assets where {field} matches regex value",
            cmd_name=method.replace("_", "-"),
            method=method,
        )
        add_cmd(grp_obj=grp_obj, method=method, cmd=cmd)

    method = "get_by_value"
    cmd = gen_get_by_cmd(
        options=[*GET_BY_VALUE_BUILDERS, GET_BY_VALUE_FIELD],
        doc="Get assets where a field equals value",
        cmd_name=method.replace("_", "-"),
        method=method,
    )
    add_cmd(grp_obj=grp_obj, method=method, cmd=cmd)

    method = "get_by_values"
    cmd = gen_get_by_cmd(
        options=[*GET_BY_VALUES_BUILDERS, GET_BY_VALUE_FIELD],
        doc="Get assets where a field equals multiple values",
        cmd_name=method.replace("_", "-"),
        method=method,
    )
    add_cmd(grp_obj=grp_obj, method=method, cmd=cmd)

    method = "get_by_value_regex"
    cmd = gen_get_by_cmd(
        options=[*GET_BY_VALUE_REGEX_BUILDERS, GET_BY_VALUE_FIELD],
        doc="Get assets where a field matches regex value",
        cmd_name=method.replace("_", "-"),
        method=method,
    )
    add_cmd(grp_obj=grp_obj, method=method, cmd=cmd)


add_cmds(grp_obj=devices, fields=["hostname", "mac", "ip"])
add_cmds(grp_obj=users, fields=["username", "mail"])

method = "get_by_subnet"
cmd = gen_get_by_cmd(
    options=GET_BY_VALUE_BUILDERS,
    doc="Get assets in subnet",
    cmd_name=method.replace("_", "-"),
    method=method,
)
add_cmd(grp_obj=devices, method=method, cmd=cmd)
