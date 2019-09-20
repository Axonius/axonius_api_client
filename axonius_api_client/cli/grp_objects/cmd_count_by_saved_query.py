# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context


@click.command(name="count-by-saved-query", context_settings=context.CONTEXT_SETTINGS)
@context.OPT_URL
@context.OPT_KEY
@context.OPT_SECRET
@click.option(
    "--name",
    "-n",
    "name",
    help="Name of saved query to get count of assets from.",
    required=True,
    show_envvar=True,
)
@context.pass_context
@click.pass_context
def cmd(clickctx, ctx, url, key, secret, name):
    """Get all objects matching a query."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    api = getattr(client, clickctx.parent.command.name)

    with context.exc_wrap(wraperror=ctx.wraperror):
        raw_data = api.count_by_saved_query(name=name)

    print(context.jdump(raw_data))
