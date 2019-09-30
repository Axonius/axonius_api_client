# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import time

import click

from .. import cli_constants, options


@click.command(name="delete", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_WAIT_DELETE
@click.option(
    "--name",
    "-n",
    "names",
    help="Name of saved query to delete.",
    multiple=True,
    required=True,
    show_envvar=True,
)
@click.pass_context
def cmd(ctx, url, key, secret, names, wait):
    """Delete a saved query."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    pp_grp = ctx.parent.parent.command.name
    api = getattr(client, pp_grp)

    rows = []
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        for name in names:
            rows.append(api.saved_query.get_by_name(value=name))

    row_names = [x["name"] for x in rows]

    msg = "In {s} second will delete saved queries: {n}"
    msg = msg.format(s=wait, n=row_names)
    ctx.obj.echo_warn(msg)

    time.sleep(wait)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        api.saved_query.delete(rows=rows)

    msg = "Successfully deleted saved queries: {n}"
    msg = msg.format(n=row_names)
    ctx.obj.echo_ok(msg)
