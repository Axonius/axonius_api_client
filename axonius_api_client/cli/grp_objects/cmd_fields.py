# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import re

import click

from .. import cli_constants, options, serial


@click.command(name="fields", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
@click.option(
    "--adapter-re",
    "-ar",
    "adapter_re",
    default=".*",
    help="Only fetch fields for adapters matching this regex.",
    metavar="REGEX",
    show_envvar=True,
)
@click.option(
    "--field-re",
    "-fr",
    "field_re",
    default=".*",
    help="Only fetch fields matching this regex.",
    metavar="REGEX",
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
    adapter_re,
    field_re,
):
    """Get the available fields (columns) for assets."""
    p_grp = ctx.parent.command.name

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    api = getattr(client, p_grp)

    adapter_rec = re.compile(adapter_re, re.I)
    field_rec = re.compile(field_re, re.I)

    raw_data = {}

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_fields = api.fields.get()

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
        ctx.obj.echo_error(msg)

    formatters = {"json": serial.to_json, "csv": to_csv}

    ctx.obj.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        joiner=export_delim,
    )


def to_csv(ctx, raw_data, **kwargs):
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

    return serial.dictwriter(rows=rows, headers=headers)
