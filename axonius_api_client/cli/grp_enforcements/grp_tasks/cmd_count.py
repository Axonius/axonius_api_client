# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import add_options
from .options_get import AUTH, OPTS_FILTERS

OPTIONS = [*AUTH, *OPTS_FILTERS]


@click.command(name="count", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Get Count of Enforcement Center Tasks matching filters."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.enforcements.tasks.count(**kwargs)
    ctx.obj.echo_ok("Count of tasks matching supplied filters:")
    click.echo(f"{data}")
    ctx.exit(0)
