# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json-full", "json"]),
    help="Format of to export data in",
    default="json",
    show_envvar=True,
    show_default=True,
)

OPTIONS = [*AUTH, EXPORT]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get all settings."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    settings_name = ctx.parent.command.name.replace("-", "_")
    settings_obj = getattr(client.system, settings_name)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = settings_obj.get()

    if export_format == "json":
        click.secho(json_dump(data["config"]))
        ctx.exit(0)

    if export_format == "json-full":
        click.secho(json_dump(data))
        ctx.exit(0)

    ctx.exit(1)
