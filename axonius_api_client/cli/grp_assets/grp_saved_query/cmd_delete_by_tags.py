# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

METHOD = "delete-by-tags"
OPTIONS = [
    *AUTH,
    click.option(
        "--tag",
        "-t",
        "value",
        help="Tags of saved queries",
        required=True,
        multiple=True,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="delete-by-tags", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Delete saved queries by tags."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = apiobj.saved_query.get_by_tags(**kwargs)
        apiobj.saved_query.delete(rows=rows)

    ctx.obj.echo_ok("Successfully deleted saved queries:")

    for row in rows:
        ctx.obj.echo_ok("  {}".format(row["name"]))

    ctx.exit(0)
