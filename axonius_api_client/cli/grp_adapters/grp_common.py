# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
# from ...api.parsers.tables import tablize_adapters
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
    "--generic/--specific",
    "-g/-s",
    "generic",
    default=True,
    show_envvar=True,
    show_default=True,
    help="Generic or adapter specific config",
)


def config_export(ctx, rows, export_format):
    """Pass."""
    if export_format == "json":
        click.secho(json_dump(rows["config"]))
    elif export_format == "json-full":
        click.secho(json_dump(rows))
    ctx.exit(0)
