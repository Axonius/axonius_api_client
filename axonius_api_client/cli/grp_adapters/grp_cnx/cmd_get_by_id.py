# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, NODE_CNX, add_options
from .grp_common import EXPORT, ID_CNX, handle_export

OPTIONS = [
    *AUTH,
    EXPORT,
    *NODE_CNX,
    ID_CNX,
]


@click.command(name="get-by-id", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get a connection by ID."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.adapters.cnx.get_by_id(**kwargs)
    handle_export(ctx=ctx, rows=rows, export_format=export_format)
