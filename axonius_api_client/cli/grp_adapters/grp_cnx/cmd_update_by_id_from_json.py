# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import CnxUpdateError
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, INPUT_FILE, NODE_CNX, add_options
from .grp_common import EXPORT, ID_CNX, SAVE_AND_FETCH, handle_export

OPTIONS = [
    *AUTH,
    EXPORT,
    SAVE_AND_FETCH,
    *NODE_CNX,
    INPUT_FILE,
    ID_CNX,
]


@click.command(name="update-by-id-from-json", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    input_file,
    adapter_node,
    adapter_name,
    cnx_id,
    save_and_fetch,
    **kwargs,
):
    """Update a connection from a JSON file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    new_config = ctx.obj.read_stream_json(stream=input_file, expect=dict)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        try:
            cnx_new = client.adapters.cnx.update_by_id(
                adapter_name=adapter_name,
                adapter_node=adapter_node,
                cnx_id=cnx_id,
                save_and_fetch=save_and_fetch,
                **new_config,
            )
            ctx.obj.echo_ok(msg="Connection updated successfully!")

        except CnxUpdateError as exc:
            ctx.obj.echo_error(msg=f"{exc}", abort=False)
            cnx_new = exc.cnx_new

    handle_export(ctx=ctx, rows=cnx_new, **kwargs)
