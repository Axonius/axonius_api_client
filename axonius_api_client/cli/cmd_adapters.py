# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import click

from . import context


@click.command("clients", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--status",
    default="all",
    help="Only fetch fields for adapters matching this regex.",
    type=click.Choice(["bad", "ok", "all"]),
    show_envvar=True,
    show_default=True,
)
@context.pass_context
@click.pass_context
def clients(
    clickctx,
    ctx,
    url,
    key,
    secret,
    export_format,
    export_file,
    export_path,
    export_overwrite,
    status,
):
    """Get all adapters with clients that have errors."""
    ctx._clickctx = clickctx
    client = ctx.start_client(url=url, key=key, secret=secret)

    data = run(ctx=ctx, client=client, export_format=export_format, status=status)

    ctx.export(
        data=data,
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
    for raw_client in raw_data:
        client = {}
        # HERE NOW
        # for k, v in raw_client.items():
        #     if isinstance(v, list):
        rows.append(client)
    return ctx.dicts_to_csv(rows=rows, headers=headers)


def run(ctx, client, export_format, status):
    """Pass."""
    if status == "bad":
        raw_data = client.adapters.get(client_bad=True, return_clients=True)
    elif status == "good":
        raw_data = client.adapters.get(client_ok=True, return_clients=True)
    else:
        raw_data = client.adapters.get(return_clients=True)

    formatters = {"json": to_json, "csv": to_csv}

    if export_format in formatters:
        data = formatters[export_format](ctx=ctx, raw_data=raw_data)
    else:
        msg = "Export format {f!r} is unsupported! Must be one of: {sf}"
        msg = msg.format(f=export_format, sf=list(formatters.keys()))
        ctx.echo_error(msg=msg)

    return data
