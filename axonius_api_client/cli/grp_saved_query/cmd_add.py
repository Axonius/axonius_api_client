# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from ... import constants
from .. import context
from . import grp_common


@click.command(name="add", context_settings=context.CONTEXT_SETTINGS)
@context.OPT_URL
@context.OPT_KEY
@context.OPT_SECRET
@context.OPT_EXPORT_FILE
@context.OPT_EXPORT_PATH
@context.OPT_EXPORT_FORMAT
@context.OPT_EXPORT_OVERWRITE
@context.OPT_QUERY
@context.OPT_FIELDS
@context.OPT_FIELDS_DEFAULT
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
    type=context.SplitEquals(),
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
@context.pass_context
@click.pass_context
def cmd(
    clickctx,
    ctx,
    url,
    key,
    secret,
    export_format,
    export_file,
    export_path,
    export_overwrite,
    name,
    query,
    fields,
    fields_default,
    sort_field,
    sort_descending,
    column_filters,
    gui_page_size,
):
    """Get a report of adapters for objects in query."""
    client = ctx.start_client(url=url, key=key, secret=secret)
    api = getattr(client, clickctx.parent.parent.command.name)

    column_filters = dict(column_filters)

    with context.exc_wrap(wraperror=ctx.wraperror):
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
    ctx.echo_ok(msg)

    formatters = {"json": context.to_json, "csv": grp_common.to_csv}

    ctx.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
    )
