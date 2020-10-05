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


@click.command(name="sizes", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get disk usage information."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.meta.historical_sizes()

    if export_format == "json":
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "str":
        click.secho(f"Disk Free MB: {data['disk_free_mb']}")
        click.secho(f"Disk Used MB: {data['disk_used_mb']}")
        ctx.exit(0)

    ctx.exit(1)
