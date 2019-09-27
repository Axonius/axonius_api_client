# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, options, serial
from ..grp_objects import grp_common as grp_obj_common


@click.command(name="missing-adapters", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
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
def cmd(
    ctx,
    url,
    key,
    secret,
    export_format,
    export_file,
    export_path,
    export_overwrite,
    export_delim,
    rows,
):
    """Get a report of missing adapters for assets."""
    rows = grp_obj_common.get_rows(ctx=ctx, rows=rows)

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    pp_grp = ctx.parent.parent.command.name
    api = getattr(client, pp_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_data = api.reports.missing_adapters(rows=rows)

    formatters = {"json": serial.to_json, "csv": serial.obj_to_csv}

    ctx.obj.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        joiner=export_delim,
    )
