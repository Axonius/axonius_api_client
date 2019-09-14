# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from ... import constants, tools
from .. import context

# TODO: Custom parameter type for key=value


@click.command("add", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@click.option(
    "--name",
    help="Name of saved query to create.",
    required=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--query",
    help="Query built from Query Wizard.",
    required=True,
    metavar="QUERY",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--field",
    help="Columns to include in the format of adapter:field.",
    metavar="ADAPTER:FIELD",
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--fields-default/--no-fields-default",
    default=True,
    help="Include default fields for this object type.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--sort-field",
    help="Column to sort data on.",
    metavar="ADAPTER:FIELD",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--sort-descending/--no-sort-descending",
    default=True,
    help="Sort --sort-field descending.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--column-filter",
    help="Columns to filter in the format of adapter:field=value.",
    metavar="ADAPTER:FIELD=value",
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--gui-page-size",
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
    name,
    query,
    field,
    fields_default,
    sort_field,
    sort_descending,
    column_filter,
    gui_page_size,
):
    """Get a report of adapters for objects in query."""
    client = ctx.start_client(url=url, key=key, secret=secret)
    api = getattr(client, clickctx.parent.parent.command.name)

    column_filters = {}

    for cf in tools.listify(column_filter):
        split = cf.split("=")

        if len(split) != 2:
            msg = "Need an '=' in --column-filter {}"
            msg = msg.format(cf)
            ctx.echo_error(msg)

        column_filters[split[0]] = split[1]

    with context.exc_wrap(wraperror=ctx.wraperror):
        raw_data = api.saved_query.add(
            name=name,
            query=query,
            fields=field,
            fields_default=fields_default,
            sort=sort_field,
            sort_descending=sort_descending,
            column_filters=column_filters,
            gui_page_size=gui_page_size,
        )

    msg = "Successfully created saved query: {n}"
    msg = msg.format(n=raw_data["name"])
    ctx.echo_ok(msg)
