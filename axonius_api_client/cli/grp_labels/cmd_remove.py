# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context


@click.command("remove", context_settings=context.CONTEXT_SETTINGS)
@context.OPT_URL
@context.OPT_KEY
@context.OPT_SECRET
@click.option(
    "--rows",
    "-r",
    "rows",
    help="The JSON data of rows returned by any get command for this object type.",
    default="-",
    type=click.File(mode="r"),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--label",
    "-l",
    "labels",
    help="Labels to add to rows.",
    required=True,
    multiple=True,
    show_envvar=True,
)
@context.pass_context
@click.pass_context
def cmd(clickctx, ctx, url, key, secret, rows, labels):
    """Get a report of adapters for objects in query."""
    client = ctx.start_client(url=url, key=key, secret=secret)
    content = context.json_from_stream(ctx=ctx, stream=rows, src="--rows")

    api = getattr(client, clickctx.parent.parent.command.name)

    with context.exc_wrap(wraperror=ctx.wraperror):
        raw_data = api.labels.remove(rows=content, labels=labels)

    print(context.to_json(raw_data))
