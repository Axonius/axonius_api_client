# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...constants.adapters import CONFIG_TYPES
from ...tools import json_dump
from ..context import click


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
