# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_EXPORT, OPT_ID_CNX, OPTS_NODE

OPTIONS = [
    *AUTH,
    *OPTS_NODE,
    OPT_ID_CNX,
    OPT_EXPORT,
]


@click.command(name="get-by-id", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, adapter_name, adapter_node, cnx_id, tunnel):
    """Get a connection by ID."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.adapters.cnx.get_by_id(
            adapter_name=adapter_name, adapter_node=adapter_node, cnx_id=cnx_id, tunnel=tunnel
        )
    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
