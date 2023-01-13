# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ....constants.api import TABLE_FORMAT
from ....parsers.tables import tablize
from ....tools import json_dump, listify
from ...context import click
from ...options import TABLE_FMT


def export_str_names(data, **kwargs):
    """Pass."""
    return "\n".join([x.name for x in listify(data)])


def export_str(data, **kwargs):
    """Pass."""
    return f"\n{'-' * 60}\n".join("\n".join(x.to_strs()) for x in listify(data))


def export_table(data, table_format=TABLE_FORMAT, **kwargs):
    """Pass."""
    return tablize(value=[x.to_tablize() for x in listify(data)], fmt=table_format)


def export_json(data, **kwargs):
    """Pass."""
    data = data[0] if isinstance(data, list) and len(data) == 1 else data
    return json_dump([x.to_dict() for x in data] if isinstance(data, list) else data.to_dict())


EXPORT_FORMATS: dict = {
    "json": export_json,
    "str-names": export_str_names,
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

OPTS_EXPORT = [
    OPT_EXPORT,
    TABLE_FMT,
]

OPT_OVERWRITE = click.option(
    "--overwrite/--no-overwrite",
    "-ow/-now",
    "overwrite",
    default=False,
    help="If a Saved Query exists with same name, overwrite it.",
    show_envvar=True,
    show_default=True,
)

OPT_UPDATE_SQ = click.option(
    "--saved-query",
    "-sq",
    "sq",
    help="Name or UUID of saved query to update",
    required=True,
    show_envvar=True,
    show_default=True,
)
OPT_SQ_SELECT_OLD = click.option(
    "--name",
    "-n",
    "value",
    help="Name or UUID of saved query",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_UPDATE_VALUE = click.option(
    "--value",
    "-v",
    "value",
    help="Value to update",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPT_UPDATE_APPEND = click.option(
    "--append/--no-append",
    "-a/-na",
    "append",
    default=False,
    help="Append supplied value to value from existing Saved Query.",
    show_envvar=True,
    show_default=True,
)

OPT_UPDATE_REMOVE = click.option(
    "--remove/--no-remove",
    "-r/-nr",
    "remove",
    default=False,
    help="Remove any supplied values from existing Saved Query.",
    show_envvar=True,
    show_default=True,
)
