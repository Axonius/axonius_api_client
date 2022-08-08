# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...api.json_api.adapters import AdapterFetchHistory
from ...constants.adapters import CONFIG_TYPES
from ...parsers.tables import tablize
from ...tools import csv_writer, json_dump
from ..context import click


def export_to_tablize(data, **kwargs):
    """Pass."""
    items = [x.to_tablize() for x in data] if isinstance(data, list) else [data.to_tablize()]
    return tablize(items)


def export_csv(data, **kwargs):
    """Pass."""
    rows = [x.to_csv() for x in data]
    columns = AdapterFetchHistory._props_csv()
    return csv_writer(rows=rows, columns=columns)


def export_json_full(data, **kwargs):
    """Pass."""
    return json_dump(data)


def export_json(data, **kwargs):
    """Pass."""
    return json_dump(data["config"])


CONFIG_EXPORT_FORMATS: dict = {
    "json": export_json,
    "json-full": export_json_full,
}


CONFIG_EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(list(CONFIG_EXPORT_FORMATS)),
    help="Format of to export data in",
    default="json",
    show_envvar=True,
    show_default=True,
)

CONFIG_TYPE = click.option(
    "--config-type",
    "-ct",
    "config_type",
    default=CONFIG_TYPES[0],
    type=click.Choice(CONFIG_TYPES),
    show_envvar=True,
    show_default=True,
    help="Type of adapter configuration to work with",
)
