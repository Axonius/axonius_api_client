# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from ... import constants
from .. import cli_constants, click_ext, options, serial
from . import grp_common


@click.command(name="add", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
@options.OPT_QUERY
@options.OPT_QUERY_FILE
@options.OPT_FIELDS
@options.OPT_FIELDS_DEFAULT
@click.option(
    "--name",
    "-n",
    "name",
    help="Name of saved query to create.",
    required=True,
    show_envvar=True,
)
@click.option(
    "--sort-field",
    "-sf",
    "sort_field",
    help="Column to sort data on.",
    metavar="ADAPTER:FIELD",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--sort-ascending",
    "-sd",
    "sort_descending",
    default=True,
    help="Sort --sort-field ascending.",
    is_flag=True,
    show_envvar=True,
)
@click.option(
    "--column-filter",
    "-cf",
    "column_filters",
    help="Columns to filter in the format of adapter:field=value.",
    metavar="ADAPTER:FIELD=value",
    type=click_ext.SplitEquals(),
    multiple=True,
    show_envvar=True,
)
@click.option(
    "--gui-page-size",
    "-gps",
    default=format(constants.GUI_PAGE_SIZES[0]),
    help="Number of rows to show per page in GUI.",
    type=click.Choice([format(x) for x in constants.GUI_PAGE_SIZES]),
    show_envvar=True,
    show_default=True,
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
    name,
    query,
    query_file,
    fields,
    fields_default,
    sort_field,
    sort_descending,
    column_filters,
    gui_page_size,
):
    """Add a saved query."""
    if query_file:
        query = query_file.read()

    column_filters = dict(column_filters)

    pp_grp = ctx.parent.parent.command.name
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    api = getattr(client, pp_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_data = api.saved_query.add(
            name=name,
            query=query,
            fields=fields,
            fields_default=fields_default,
            sort=sort_field,
            sort_descending=sort_descending,
            column_filters=column_filters,
            gui_page_size=gui_page_size,
        )

    msg = "Successfully created saved query: {n}"
    msg = msg.format(n=raw_data["name"])
    ctx.obj.echo_ok(msg)

    formatters = {"json": serial.to_json, "csv": grp_common.to_csv}

    ctx.obj.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        joiner=export_delim,
    )
