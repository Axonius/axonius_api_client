# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context
from . import grp_common


@click.command("get-by-subnet", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--value",
    "-v",
    help="Value to search for.",
    required=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--query",
    "-q",
    help="Query to add to the end of the query built to search for --value.",
    default="",
    metavar="QUERY",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--field",
    "-f",
    help="Columns to include in the format of adapter:field.",
    metavar="ADAPTER:FIELD",
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--fields-default/--no-fields-default",
    "-fd/-nfd",
    default=True,
    help="Include default columns for this object type.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--max-rows", "-mr", help="Only return this many rows.", type=click.INT, hidden=True
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
    value,
    query,
    field,
    fields_default,
    max_rows,
):
    """Get all objects matching a query."""
    grp_common.get_by_cmd(
        clickctx=clickctx,
        ctx=ctx,
        url=url,
        key=key,
        secret=secret,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        value=value,
        query=query,
        field=field,
        fields_default=fields_default,
        max_rows=max_rows,
        method="get_by_subnet",
    )
