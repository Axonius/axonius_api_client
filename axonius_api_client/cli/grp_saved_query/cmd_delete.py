# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import time

import click

from ... import tools
from .. import context


@click.command("delete", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@click.option(
    "--rows",
    "-r",
    help="JSON rows returned by any get command for saved queries of this object type.",
    default="-",
    type=click.File(mode="r"),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--wait",
    "-w",
    help="Wait this many seconds before deleting",
    default=30,
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@context.pass_context
@click.pass_context
def cmd(clickctx, ctx, url, key, secret, rows, wait):
    """Get a report of adapters for objects in query."""
    client = ctx.start_client(url=url, key=key, secret=secret)
    content = context.json_from_stream(ctx=ctx, stream=rows, src="--rows")
    content = tools.listify(obj=content, dictkeys=False)
    names = tools.join_comma([x["name"] for x in content])

    msg = "In {s} second will delete saved queries: {n}"
    msg = msg.format(s=wait, n=names)
    ctx.echo_warn(msg)

    time.sleep(wait)

    api = getattr(client, clickctx.parent.parent.command.name)

    with context.exc_wrap(wraperror=ctx.wraperror):
        api.saved_query.delete(rows=content)

    msg = "Successfully deleted saved queries: {n}"
    msg = msg.format(n=names)
    ctx.echo_ok(msg)
