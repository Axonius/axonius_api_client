# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....constants.api import TABLE_FORMAT
from ....parsers.tables import tablize
from ....tools import json_dump, listify
from ...context import click
from ...options import TABLE_FMT


def export_str(data, **kwargs):
    """Pass."""
    return "\n\n".join(str(x) for x in listify(data))


def export_table(data, table_format=TABLE_FORMAT, **kwargs):
    """Pass."""
    return tablize(value=[x.to_tablize() for x in listify(data)], fmt=table_format)


def export_json(data, **kwargs):
    """Pass."""
    return json_dump([x.to_dict() for x in data] if isinstance(data, list) else data.to_dict())


EXPORT_FORMATS: dict = {
    "json": export_json,
    "str": export_str,
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

OPTS_EXPORT = [OPT_EXPORT, TABLE_FMT]

OPT_VALUE = click.option(
    "--value",
    "-v",
    "value",
    help="Name or UUID of data scope",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_UPDATE = click.option(
    "--update",
    "-up",
    "update",
    help="Name or UUID of Asset Scope (multiple)",
    multiple=True,
    required=True,
    show_envvar=True,
    show_default=True,
)
OPT_APPEND = click.option(
    "--append/--no-append",
    "-a/-na",
    "append",
    required=False,
    default=False,
    help="Append supplied asset scopes instead of overwriting",
    show_envvar=True,
    show_default=True,
)
OPT_REMOVE = click.option(
    "--remove/--no-remove",
    "-r/-nr",
    "remove",
    required=False,
    default=False,
    help="Remove supplied asset scopes instead of overwriting or appending",
    show_envvar=True,
    show_default=True,
)
OPTS_UPDATE_SCOPE = [OPT_UPDATE, OPT_APPEND, OPT_REMOVE]
