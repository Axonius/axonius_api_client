# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, options, serial


@click.command(name="count", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_QUERY
@click.pass_context
def cmd(ctx, url, key, secret, query):
    """Get the count of assets from a query."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.command.name
    api = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_data = api.count(query=query)

    print(serial.to_json(ctx=ctx, raw_data=raw_data))
