# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import click

EXPORT = [
    click.option(
        "--export-format",
        "-xf",
        "export_format",
        type=click.Choice(["json-raw", "json", "str"]),
        help="Format to export data in",
        default="str",
        show_envvar=True,
        show_default=True,
    )
]


def join(obj):
    """Pass."""
    return "\n - " + "\n - ".join(obj)


def handle_export(ctx, data, export_format, **kwargs):
    """Pass."""
    if export_format == "json":
        click.secho(json_dump(data.to_dict()))
        ctx.exit(0)

    if export_format == "json-raw":
        click.secho(json_dump(data.raw))
        ctx.exit(0)

    if export_format == "str":
        lines = []

        props = data.to_str_properties()
        lines += [f"Properties:{join(props)}"]

        click.secho("\n".join(lines))

        ctx.exit(0)

    ctx.exit(1)
