# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

import click

from . import context
from .. import tools


@click.command("fields", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--adapter-re",
    default=".*",
    help="Only fetch fields for adapters matching this regex.",
    metavar="REGEX",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--field-re",
    default=".*",
    help="Only fetch fields matching this regex.",
    metavar="REGEX",
    show_envvar=True,
    show_default=True,
)
@context.pass_context
@click.pass_context
def fields(
    clickctx,
    ctx,
    url,
    key,
    secret,
    export_format,
    export_file,
    export_path,
    export_overwrite,
    adapter_re,
    field_re,
):
    """Get the fields/columns for all adapters."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    api = getattr(client, clickctx.parent.command.name)

    adapter_rec = re.compile(adapter_re, re.I)
    field_rec = re.compile(field_re, re.I)

    try:
        raw_fields = api.fields.get()
    except Exception as exc:
        if ctx.wraperror:
            ctx.echo_error(format(exc))
        raise

    raw_data = {}

    for adapter, adapter_fields in raw_fields.items():
        if not adapter_rec.search(adapter):
            continue

        for field, field_into in adapter_fields.items():
            if not field_rec.search(field):
                continue
            raw_data[adapter] = raw_data.get(adapter, [])
            raw_data[adapter].append(field)

    if not raw_data:
        msg = "No fields found matching adapter regex {are!r} and field regex {fre!r}"
        msg = msg.format(are=adapter_re, fre=field_re)
        ctx.echo_error(msg)

    formatters = {"json": ctx.to_json, "csv": fields_to_csv}

    ctx.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
    )

    return ctx


@click.command("adapters", context_settings=context.CONTEXT_SETTINGS)
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
def adapters(
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

    formatters = {"json": ctx.to_json, "csv": adapters_to_csv}

    ctx.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
    )
    return ctx


def adapters_to_csv(ctx, raw_data, **kwargs):
    """Pass."""
    rows = []
    headers = []
    for raw_row in raw_data:
        row = {}
        for k, v in raw_row.items():
            if k not in headers:
                headers.append(k)

            if isinstance(v, (list, tuple)):
                row[k] = tools.crjoin(v, j="\n", pre="")
            else:
                row[k] = v
        import json

        print(json.dumps(row, indent=2))
        rows.append(row)
        break
    headers = sorted(headers, reverse=True)
    return ctx.dicts_to_csv(rows=rows, headers=headers)


def fields_to_csv(ctx, raw_data, **kwargs):
    """Pass."""
    rows = []
    headers = []
    for adapter, fields in raw_data.items():
        headers.append(adapter)
        for idx, field in enumerate(fields):
            if len(rows) < idx + 1:
                rows.append({})
            row_data = {adapter: field}
            rows[idx].update(row_data)
    return ctx.dicts_to_csv(rows=rows, headers=headers)
