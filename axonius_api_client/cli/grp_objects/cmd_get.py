# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context


@click.command("get", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--query",
    "-q",
    help="Query built from Query Wizard to filter objects (empty returns all).",
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
    help="Include default fields for this object type.",
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
    query,
    field,
    fields_default,
    max_rows,
):
    """Get all objects matching a query."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    api = getattr(client, clickctx.parent.command.name)

    with context.exc_wrap(wraperror=ctx.wraperror):
        raw_data = api.get(
            query=query, fields=field, fields_default=fields_default, max_rows=max_rows
        )

    formatters = {"json": context.to_json, "csv": context.obj_to_csv}

    ctx.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
    )
