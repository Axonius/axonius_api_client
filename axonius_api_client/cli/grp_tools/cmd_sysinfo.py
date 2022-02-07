# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...tools import json_dump, sysinfo
from ..context import CONTEXT_SETTINGS
from ..options import add_options


def export_str(data, **kwargs):
    """Pass."""
    return "\n".join([f"{k}: {v}" for k, v in data.items()])


def export_json(data, **kwargs):
    """Pass."""
    return json_dump(data)


EXPORT_FORMATS: dict = {
    "json": export_json,
    "str": export_str,
}

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(list(EXPORT_FORMATS)),
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
    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
