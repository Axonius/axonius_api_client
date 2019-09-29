# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, options, serial
from . import grp_common


@click.command(name="discover", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_INCLUDE_SETTINGS
@options.OPT_EXPORT_DELIM
@options.OPT_NO_ERROR
@click.option(
    "--show-sources",
    "-ss",
    help="Print the source commands that can be supplied as valid input to -r/--rows.",
    default=False,
    is_flag=True,
    is_eager=True,
    callback=grp_common.show_sources,
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
    error,
    include_settings,
):
    """Start a discovery (fetch) for an adapter connection."""
    rows = grp_common.get_rows(ctx=ctx, rows=rows)

    processed = []

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    found_error = False

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        for cnx in rows:
            raw_data = client.adapters.cnx.update(cnx=cnx, error=False)

            action = "discovering"
            had_error, had_cnx_error = grp_common.handle_response(
                ctx=ctx, cnx=raw_data, action=action, cnx_error=True
            )

            processed.append(raw_data)

            if had_error or had_cnx_error:
                found_error = True
                if error:
                    break

    formatters = {"json": serial.to_json, "csv": grp_common.to_csv}

    ctx.obj.handle_export(
        raw_data=processed,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        joiner=export_delim,
        include_settings=include_settings,
    )

    ctx.exit(int(found_error))
