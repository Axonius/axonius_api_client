# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, options, serial
from ..grp_objects import grp_common as grp_obj_common


@click.command(name="add", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_LABELS
@click.option(
    "--show-sources",
    "-ss",
    help="Print the source commands that can be supplied as valid input to -r/--rows.",
    default=False,
    is_flag=True,
    is_eager=True,
    callback=grp_obj_common.show_sources,
    expose_value=False,
)
@options.OPT_ROWS
@click.pass_context
def cmd(ctx, url, key, secret, rows, labels):
    """Add labels (tags) to assets."""
    rows = grp_obj_common.get_rows(ctx=ctx, rows=rows)

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    pp_grp = ctx.parent.parent.command.name
    api = getattr(client, pp_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_data = api.labels.add(rows=rows, labels=labels)

    print(serial.to_json(ctx=ctx, raw_data=raw_data))
