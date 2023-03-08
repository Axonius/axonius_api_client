# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

OPTIONS = [*AUTH]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, value):
    """Get Folders."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.folders.queries.get(value=value)
        print(data)

    # click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
