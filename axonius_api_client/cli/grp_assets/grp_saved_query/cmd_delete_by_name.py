# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

OPTIONS = [
    *AUTH,
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


@click.command(name="delete-by-name", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Delete a saved query by name."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = apiobj.saved_query.get_by_name(**kwargs)
        apiobj.saved_query.delete(rows=rows)

    ctx.obj.echo_ok("Successfully deleted saved query: rows['name']")

    ctx.exit(0)
