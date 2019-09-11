# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import tools
from . import context


@click.command("missing-adapters", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--query",
    help="Only report on objects matching this query.",
    metavar="QUERY",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--others-not-seen",
    default=False,
    help="Include adapters that other objects have not seen.",
    type=click.BOOL,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--unconfigured",
    default=False,
    help="Include adapters that have no clients configured.",
    type=click.BOOL,
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
    query,
    others_not_seen,
    unconfigured,
):
    """Get a report of adapters for objects in query."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    api = getattr(client, clickctx.parent.command.name)

    serial_dates = True
    serial_lines = not export_format == "json"

    try:
        raw_data = api.reports.adapters(
            query=query,
            serial_dates=serial_dates,
            serial_lines=serial_lines,
            others_not_seen=others_not_seen,
            unconfigured=unconfigured,
        )
    except Exception as exc:
        if ctx.wraperror:
            ctx.echo_error(format(exc))
        raise

    formatters = {"json": ctx.to_json, "csv": to_csv}

    ctx.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
    )
    return ctx


def to_csv(ctx, raw_data, **kwargs):
    """Pass."""
    rows = []
    headers = []

    for raw_row in raw_data:
        row = {}
        rows.append(row)

        for k, v in raw_row.items():
            if k not in headers:
                headers.append(k)

            row[k] = tools.join.cr(v, pre=False) if tools.is_list(v) else v

    headers = sorted(headers, reverse=True)
    return tools.csv.cereal(rows=rows, headers=headers)
