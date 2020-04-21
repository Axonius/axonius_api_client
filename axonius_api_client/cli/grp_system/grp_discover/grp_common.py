# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import click

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json-full", "json", "str"]),
    help="Format of to export data in",
    default="str",
    show_envvar=True,
    show_default=True,
)


def handle_export(ctx, data, export_format, **kwargs):
    """Pass."""
    if export_format == "json":
        data.pop("phases")
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "json-full":
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "str":
        data.pop("phases")
        for k, v in data.items():
            k = k.replace("_", " ").title()
            if isinstance(v, list):
                v = ", ".join(v)
            click.secho(f"{k}: {v}")
        ctx.exit(0)

    ctx.exit(1)
