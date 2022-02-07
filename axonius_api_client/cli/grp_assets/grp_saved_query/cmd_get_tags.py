# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import listify
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

OPTIONS = [*AUTH]


@click.command(name="get-tags", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Get all known tags for saved queries."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = listify(apiobj.saved_query.get_tags(**kwargs))

    ctx.obj.echo_ok(f"Successfully fetched {len(data)} saved query tags")
    click.secho("\n".join(data))
    ctx.exit(0)
