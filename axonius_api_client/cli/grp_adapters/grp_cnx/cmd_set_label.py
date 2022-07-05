# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....exceptions import CnxUpdateError
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_EXPORT, OPT_ID_CNX, OPT_SAVE_AND_FETCH, OPTS_NODE

OPTIONS = [
    *AUTH,
    *OPTS_NODE,
    OPT_SAVE_AND_FETCH,
    OPT_ID_CNX,
    click.option(
        "--label",
        "-l",
        "label",
        help="New label to set for connection.",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    OPT_EXPORT,
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
    tunnel,
    cnx_id,
    label,
    save_and_fetch,
    export_format,
):
    """Set the label for a connection."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    had_error = False
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        cnx = client.adapters.cnx.get_by_id(
            adapter_name=adapter_name,
            adapter_node=adapter_node,
            tunnel=tunnel,
            cnx_id=cnx_id,
        )
        try:
            data = client.adapters.cnx.set_cnx_label(
                cnx=cnx, value=label, save_and_fetch=save_and_fetch
            )
            ctx.obj.echo_ok(msg="Connection updated with no errors")
        except CnxUpdateError as exc:  # pragma: no cover
            had_error = True
            ctx.obj.echo_error(msg=f"Connection updated with error: {exc}", abort=False)
            data = exc.cnx_new
            if not ctx.obj.wraperror:  # pragma: no cover
                raise

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(100 if had_error else 0)
