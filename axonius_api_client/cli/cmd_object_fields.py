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
    adapter_re,
    field_re,
):
    """Get the fields (columns) for all adapters."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    api = getattr(client, clickctx.parent.command.name)

    adapter_rec = re.compile(adapter_re, re.I)
    field_rec = re.compile(field_re, re.I)

    raw_fields = api.fields()

    adapters = {}
    adapters.update(raw_fields["specific"])

    gen_fields = []
    for field in raw_fields["generic"]:
        new_field = {}
        new_field.update(field)
        new_field["name"] = tools.lstrip(new_field["name"], "specific_data.data.")
        gen_fields.append(new_field)

    adapters.update({"generic": gen_fields})

    raw_data = {}

    for adapter, adapter_fields in adapters.items():
        field_trim = "adapters_data.{}.".format(adapter)
        adapter = tools.rstrip(obj=adapter, postfix="_adapter")

        if not adapter_rec.search(adapter):
            continue

        for adapter_field in adapter_fields:
            field_name = tools.lstrip(adapter_field["name"], field_trim)
            if not field_rec.search(field_name):
                continue
            raw_data[adapter] = raw_data.get(adapter, [])
            raw_data[adapter].append(field_name)

    if not raw_data:
        msg = "No fields found matching adapter regex {are!r} and field regex {fre!r}"
        msg = msg.format(are=adapter_re, fre=field_re)
        ctx.echo_error(msg)

    formatters = {"json": to_json, "csv": to_csv}

    ctx.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
    )

    return ctx


def to_json(ctx, raw_data):
    """Pass."""
    return ctx.to_json(raw_data)


def to_csv(ctx, raw_data):
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
