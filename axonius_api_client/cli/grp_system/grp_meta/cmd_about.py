# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

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

OPTIONS = [
    *AUTH,
    EXPORT,
]


@click.command(name="about", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get instance version information."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.meta.about()

    if export_format == "json":
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "str":
        for k, v in data.items():
            k = k.replace("_", " ").title()
            click.secho(f"{k}: {v}")
        ctx.exit(0)

    ctx.exit(1)
