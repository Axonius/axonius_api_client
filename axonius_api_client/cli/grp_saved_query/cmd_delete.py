# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import time

import click

from ... import tools
from .. import cli_constants, options, serial


@click.command(name="delete", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_WAIT_DELETE
@options.OPT_ROWS
@click.pass_context
def cmd(ctx, url, key, secret, rows, wait):
    """Delete a saved query."""
    pp_grp = ctx.parent.parent.command.name
    p_grp = ctx.parent.command.name
    grp = ctx.command.name

    this_grp = "{pp} {p} {g}".format(pp=pp_grp, p=p_grp, g=grp)
    this_cmd = "{tg} --rows".format(tg=this_grp)

    src_cmds = ["{pp} {p} get", "{pp} {p} get-by-name", "{pp} {p} add"]
    src_cmds = [x.format(pp=pp_grp, p=p_grp) for x in src_cmds]

    rows = serial.json_to_rows(
        ctx=ctx, stream=rows, this_cmd=this_cmd, src_cmds=src_cmds
    )

    serial.check_rows_type(
        ctx=ctx, rows=rows, this_cmd=this_cmd, src_cmds=src_cmds, all_items=True
    )

    serial.ensure_keys(
        ctx=ctx,
        rows=rows,
        this_cmd=this_cmd,
        src_cmds=src_cmds,
        keys=["name", "uuid"],
        all_items=True,
    )

    names = tools.join_comma([x["name"] for x in rows])

    msg = "In {s} second will delete saved queries: {n}"
    msg = msg.format(s=wait, n=names)
    ctx.obj.echo_warn(msg)

    time.sleep(wait)

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    api = getattr(client, pp_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        api.saved_query.delete(rows=rows)

    msg = "Successfully deleted saved queries: {n}"
    msg = msg.format(n=names)
    ctx.obj.echo_ok(msg)
