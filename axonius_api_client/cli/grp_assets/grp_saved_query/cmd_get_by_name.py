# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMAT, handle_export

OPTIONS = [
    *AUTH,
    EXPORT_FORMAT,
    click.option(
        "--name",
        "-n",
        "value",
        help="Name of saved query",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="get-by-name", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get saved queries by name."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = apiobj.saved_query.get_by_name(**kwargs)

    handle_export(ctx=ctx, rows=rows, export_format=export_format)
