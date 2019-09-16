# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context


@click.command("missing-adapters", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--rows",
    "-r",
    help="The JSON data of rows returned by any get command for this object type.",
    default="-",
    type=click.File(mode="r"),
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
    rows,
):
    """Get a report of adapters for objects in query."""
    client = ctx.start_client(url=url, key=key, secret=secret)
    content = context.json_from_stream(ctx=ctx, stream=rows, src="--rows")

    api = getattr(client, clickctx.parent.parent.command.name)

    with context.exc_wrap(wraperror=ctx.wraperror):
        raw_data = api.reports.missing_adapters(rows=content)

    formatters = {"json": context.to_json, "csv": context.obj_to_csv}

    ctx.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
    )
