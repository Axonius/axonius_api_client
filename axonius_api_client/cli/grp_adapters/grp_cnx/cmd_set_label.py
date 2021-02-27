# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import CnxUpdateError
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, NODE_CNX, add_options
from .grp_common import EXPORT, ID_CNX, SAVE_AND_FETCH, handle_export

OPTIONS = [
    *AUTH,
    EXPORT,
    SAVE_AND_FETCH,
    *NODE_CNX,
    ID_CNX,
    click.option(
        "--label",
        "-l",
        "label",
        help="Prompt for optional items that are not supplied.",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="set-label", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    adapter_node,
    adapter_name,
    cnx_id,
    label,
    save_and_fetch,
    **kwargs,
):
    """Set the label for a connection."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        try:
            cnx = client.adapters.cnx.get_by_id(
                adapter_name=adapter_name,
                adapter_node=adapter_node,
                cnx_id=cnx_id,
            )
            cnx_new = client.adapters.cnx.set_cnx_label(
                cnx=cnx, value=label, save_and_fetch=save_and_fetch
            )
            ctx.obj.echo_ok(msg="Connection updated successfully!")
        except CnxUpdateError as exc:
            ctx.obj.echo_error(msg=f"{exc}", abort=False)
            cnx_new = exc.cnx_new

    handle_export(ctx=ctx, rows=cnx_new, **kwargs)
