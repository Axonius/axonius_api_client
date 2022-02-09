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
    p_grp = ctx.parent.command.name
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = getattr(client, p_grp)
    apimethod = apiobj.labels.get
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apimethod()
    ctx.obj.echo_ok(f"Fetched {len(data)} tags")
    content = "\n".join(data)
    click.secho(content)
    ctx.exit(0)
