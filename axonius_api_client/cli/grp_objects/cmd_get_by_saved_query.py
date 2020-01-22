# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, options, serial
from . import grp_common


@click.command(
    name="get-by-saved-query", context_settings=cli_constants.CONTEXT_SETTINGS
)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
@options.OPT_EXPORT_TABLE_FORMAT
@options.OPT_FIELDS
@options.OPT_FIELDS_REGEX
@options.OPT_MAX_ROWS
@click.option(
    "--name",
    "-n",
    help="Name of saved query to get assets from.",
    required=True,
    show_envvar=True,
)
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
    export_table_format,
    fields,
    fields_regex,
    name,
    max_rows,
):
    """Get assets from a saved query."""
    p_grp = ctx.parent.command.name

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    api = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_data = api.get_by_saved_query(
            name=name, fields=fields, fields_regex=fields_regex, max_rows=max_rows
        )

    grp_common.echo_response(ctx=ctx, raw_data=raw_data, api=api)

    formatters = {"json": serial.to_json, "csv": serial.obj_to_csv}

    ctx.obj.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        export_table_format=export_table_format,
        joiner=export_delim,
    )
