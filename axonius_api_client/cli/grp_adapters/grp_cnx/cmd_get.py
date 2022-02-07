# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, NODE_CNX, add_options
from .grp_common import EXPORT_FORMATS, OPT_EXPORT

OPTIONS = [
    *AUTH,
    *NODE_CNX,
    OPT_EXPORT,
]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, adapter_node, adapter_name):
    """Get connections."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.adapters.cnx.get_by_adapter(
            adapter_name=adapter_name, adapter_node=adapter_node
        )
    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
