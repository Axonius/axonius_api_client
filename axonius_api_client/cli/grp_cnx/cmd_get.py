# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context
from . import grp_common


@click.command("get", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--rows",
    "-r",
    help="The output from 'adapters get' supplied as a file or via stdin.",
    default="-",
    type=click.File(mode="r"),
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--id",
    "-i",
    "ids",
    help="Only include connections with matching IDs.",
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--working/--no-working",
    "-w/-nw",
    help="Include connections that are working.",
    default=True,
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--broken/--no-broken",
    "-b/-nb",
    help="Include connections that are broken.",
    default=True,
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--include-settings/--no-include-settings",
    "-is/-nis",
    help="Include connection settings in CSV export.",
    default=False,
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@context.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    export_format,
    export_file,
    export_path,
    export_overwrite,
    rows,
    ids,
    working,
    broken,
    include_settings,
):
    """Get all adapters with clients that have errors."""
    client = ctx.start_client(url=url, key=key, secret=secret)
    content = context.json_from_stream(ctx=ctx, stream=rows, src="--rows")

    cnxs = []
    for adapter in content:
        if "cnx" not in adapter:
            msg = "No 'cnx' key found in adapter with keys: {k}"
            msg = msg.format(k=list(adapter))
            ctx.echo_error(msg)
        cnxs += adapter["cnx"]

    msg = "Loaded {nc} connections from {na} adapters"
    msg = msg.format(nc=len(cnxs), na=len(content))
    ctx.echo_ok(msg)

    statuses = []

    if working:
        statuses.append(True)

    if broken:
        statuses.append(False)

    with context.exc_wrap(wraperror=ctx.wraperror):
        by_statuses = client.adapters.cnx.filter_by_status(cnxs=cnxs, value=statuses)
        context.check_empty(
            ctx=ctx,
            this_data=by_statuses,
            prev_data=cnxs,
            value_type="connection statuses",
            value=statuses,
            objtype="connections",
            known_cb=ctx.obj.adapters.cnx.get_known,
            known_cb_key="cnxs",
        )

        by_ids = client.adapters.cnx.filter_by_ids(cnxs=by_statuses, value=ids)
        context.check_empty(
            ctx=ctx,
            this_data=by_ids,
            prev_data=by_statuses,
            value_type="connection ids",
            value=ids,
            objtype="connections",
            known_cb=ctx.obj.adapters.cnx.get_known,
            known_cb_key="cnxs",
        )

    formatters = {"json": context.to_json, "csv": grp_common.to_csv}

    ctx.handle_export(
        raw_data=by_ids,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        include_settings=include_settings,
    )
