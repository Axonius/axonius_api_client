# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...tools import json_dump, sysinfo
from ..context import CONTEXT_SETTINGS
from ..options import add_options

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json", "str"]),
    help="Format of to export data in",
    default="str",
    show_envvar=True,
    show_default=True,
)

OPTIONS = [EXPORT]


@click.command(name="sysinfo", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, export_format):
    """Print out system and python information."""
    data = sysinfo()

    if export_format == "str":
        for k, v in data.items():
            click.secho(f"{k}: {v}")
        ctx.exit(0)

    if export_format == "json":
        click.secho(json_dump(data))
        ctx.exit(0)

    ctx.exit(1)
