# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

OPTIONS = [*AUTH]


@click.command(name="get-tags", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Get all known tags."""
    # handler(ctx=ctx, url=url, key=key, secret=secret, **kwargs)
    p_grp = ctx.parent.command.name

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = getattr(client, p_grp)
    apimethod = apiobj.labels.get

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = apimethod()

    for row in rows:
        click.secho(row)
