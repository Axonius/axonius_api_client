# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options


def export_str(data, **kwargs):
    """Pass."""
    data = {k.replace("_", " ").title(): v for k, v in data.items()}
    data = [f"{k}: {v}" for k, v in data.items()]
    return "\n".join(data)


def export_json(data, **kwargs):
    """Pass."""
    return json_dump(data)


EXPORT_FORMATS: dict = {
    "json": export_json,
    "str": export_str,
}


OPT_EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(list(EXPORT_FORMATS)),
    help="Format of to export data in",
    default="str",
    show_envvar=True,
    show_default=True,
)

OPTIONS = [
    *AUTH,
    OPT_EXPORT,
]


@click.command(name="about", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format):
    """Get instance version information."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.meta.about()

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
