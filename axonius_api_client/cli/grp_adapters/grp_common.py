# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...constants.adapters import CONFIG_TYPES
from ...tools import json_dump
from ..context import click

CONFIG_EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json-full", "json"]),
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


def config_export(ctx, rows, export_format):
    """Pass."""
    if export_format == "json":
        click.secho(json_dump(rows["config"]))
    elif export_format == "json-full":
        click.secho(json_dump(rows))
    ctx.exit(0)
