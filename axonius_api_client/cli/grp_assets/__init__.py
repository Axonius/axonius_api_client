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
]

for cmd in CMDS:
    users.add_command(cmd)
    devices.add_command(cmd)


def add_cmds(grp_obj, fields):
    """Pass."""
    for field in fields:
        grp_obj.add_command(
            gen_get_by_cmd(
                options=GET_BY_VALUE_BUILDERS,
                doc=f"Get assets where {field} equals value",
                cmd_name=f"get-by-{field}",
                method=f"get_by_{field}",
            )
        )

        grp_obj.add_command(
            gen_get_by_cmd(
                options=GET_BY_VALUES_BUILDERS,
                doc=f"Get assets where {field} equals multiple values",
                cmd_name=f"get-by-{field}s",
                method=f"get_by_{field}s",
            )
        )

        grp_obj.add_command(
            gen_get_by_cmd(
                options=GET_BY_VALUE_REGEX_BUILDERS,
                doc=f"Get assets where {field} matches regex value",
                cmd_name=f"get-by-{field}-regex",
                method=f"get_by_{field}_regex",
            )
        )

    grp_obj.add_command(
        gen_get_by_cmd(
            options=[*GET_BY_VALUE_BUILDERS, GET_BY_VALUE_FIELD],
            doc="Get assets where a field equals value",
            cmd_name="get-by-value",
            method="get_by_value",
        )
    )

    grp_obj.add_command(
        gen_get_by_cmd(
            options=[*GET_BY_VALUES_BUILDERS, GET_BY_VALUE_FIELD],
            doc="Get assets where a field equals multiple values",
            cmd_name="get-by-values",
            method="get_by_values",
        )
    )

    grp_obj.add_command(
        gen_get_by_cmd(
            options=[*GET_BY_VALUE_REGEX_BUILDERS, GET_BY_VALUE_FIELD],
            doc="Get assets where a field matches regex value",
            cmd_name="get-by-value-regex",
            method="get_by_value_regex",
        )
    )


add_cmds(grp_obj=devices, fields=["hostname", "mac", "ip"])
add_cmds(grp_obj=users, fields=["username", "mail"])

devices.add_command(
    gen_get_by_cmd(
        options=GET_BY_VALUE_BUILDERS,
        doc="Get assets in subnet",
        cmd_name="get-by-subnet",
        method="get_by_subnet",
    )
)
