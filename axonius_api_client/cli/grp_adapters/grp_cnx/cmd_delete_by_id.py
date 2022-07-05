# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_DELETE_ENTITIES, OPT_EXPORT, OPT_ID_CNX, OPTS_NODE

OPTIONS = [
    *AUTH,
    *OPTS_NODE,
    OPT_DELETE_ENTITIES,
    OPT_EXPORT,
    OPT_ID_CNX,
]


@click.command(name="delete-by-id", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    cnx_id,
    adapter_name,
    adapter_node,
    tunnel,
    export_format,
    delete_entities,
):
    """Delete a connection by ID."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.adapters.cnx.get_by_id(
            adapter_name=adapter_name,
            adapter_node=adapter_node,
            cnx_id=cnx_id,
            tunnel=tunnel,
        )
        ret = client.adapters.cnx.delete_cnx(cnx_delete=data, delete_entities=delete_entities)

    ctx.obj.echo_ok(f"Connection deleted! (assets deleted={delete_entities})\n{ret}")
    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
