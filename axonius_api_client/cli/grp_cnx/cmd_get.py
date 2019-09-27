# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, options, serial
from . import grp_common


@click.command(name="get", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
@options.OPT_INCLUDE_SETTINGS
@click.option(
    "--id",
    "-i",
    "ids",
    help="Only include connections with matching IDs.",
    multiple=True,
    show_envvar=True,
)
@click.option(
    "--no-working",
    "-nw",
    "working",
    help="Exclude connections that are working.",
    default=True,
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--no-broken",
    "-nb",
    "broken",
    help="Include connections that are broken.",
    default=True,
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--show-sources",
    "-ss",
    help="Print the source commands that can be supplied as valid input to -r/--rows.",
    default=False,
    is_flag=True,
    is_eager=True,
    callback=grp_common.show_sources_parent,
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
    ids,
    working,
    broken,
    include_settings,
):
    """Get connections from adapters based on id or status."""
    rows = grp_common.get_rows(ctx=ctx, rows=rows, only_parent=True)

    statuses = []

    if working:
        statuses.append(True)

    if broken:
        statuses.append(False)

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        by_statuses = client.adapters.cnx.filter_by_status(cnxs=rows, value=statuses)
        grp_common.check_empty(
            ctx=ctx,
            this_data=by_statuses,
            prev_data=rows,
            value_type="connection statuses",
            value=statuses,
            objtype="connections",
            known_cb=client.adapters.cnx.get_known,
            known_cb_key="cnxs",
        )

        by_ids = client.adapters.cnx.filter_by_ids(cnxs=by_statuses, value=ids)
        grp_common.check_empty(
            ctx=ctx,
            this_data=by_ids,
            prev_data=by_statuses,
            value_type="connection ids",
            value=ids,
            objtype="connections",
            known_cb=client.adapters.cnx.get_known,
            known_cb_key="cnxs",
        )

    formatters = {"json": serial.to_json, "csv": grp_common.to_csv}

    ctx.obj.handle_export(
        raw_data=by_ids,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        joiner=export_delim,
        include_settings=include_settings,
    )
