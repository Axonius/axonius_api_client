# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, grp_objects, options, serial


@click.command(name="remove", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_ROWS
@options.OPT_LABELS
@click.pass_context
def cmd(ctx, url, key, secret, rows, labels):
    """Remove labels (tags) from assets."""
    rows = grp_objects.grp_common.get_rows(ctx=ctx, rows=rows)

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    pp_grp = ctx.parent.parent.command.name
    api = getattr(client, pp_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_data = api.labels.remove(rows=rows, labels=labels)

    print(serial.to_json(ctx=ctx, raw_data=raw_data))
