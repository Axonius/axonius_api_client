# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from . import context


@click.command("get", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--name",
    help="Only adapters matching this regex.",
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--node",
    help="Only adapters on nodes matching this regex.",
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--client-status",
    help="Only adapters with clients that are ok if True or bad if False.",
    type=click.BOOL,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--client-min",
    help="Only adapters with at least N clients.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--client-max",
    help="Only adapters with at most N clients.",
    type=click.INT,
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
    name,
    node,
    client_status,
    client_min,
    client_max,
):
    """Get all adapters with clients that have errors."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    try:
        raw_data = client.adapters.get(
            names=name or None,
            nodes=node or None,
            client_status=client_status,
            client_min=client_min,
            client_max=client_max,
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
    msg = "Data structures for Adapters are too complex to turn into CSV, use JSON!"
    ctx.echo_error(msg)
