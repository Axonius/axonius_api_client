# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import click

from .. import tools
from . import context


@click.command("get-clients", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--name",
    help="Only clients for adapters matching this regex.",
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--node",
    help="Only clients for adapters on nodes matching this regex.",
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--status",
    help="Only clients with a success if True or error if False.",
    type=click.BOOL,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--within",
    help="Only clients fetched in past N minutes.",
    type=click.INT,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--not-within",
    help="Only clients NOT fetched in past N minutes.",
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
    status,
    name,
    node,
    within,
    not_within,
):
    """Get all adapters with clients that have errors."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    try:
        raw_data = client.adapters.clients.get(
            names=name or None,
            nodes=node or None,
            status=status,
            within=within,
            not_within=not_within,
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
    headers = [
        "adapter",
        "adapter_features",
        "adapter_status",
        "status",
        "status_bool",
        "node_name",
        "node_id",
        "client_id",
        "uuid",
        "date_fetched",
    ]

    end = ["error", "settings"]

    found = []

    stmpl = "{} = {}".format

    for client in raw_data:
        settings = client.get("settings", []) or []
        settings = [stmpl(k, v["value"]) for k, v in settings.items()]
        client["settings"] = settings

        for k, v in client.items():
            found.append(k)

            v = tools.join.cr(tools.listify(v, otype=None, itype=None), pre=False)
            client[k] = v

            if k not in headers + end:
                headers.append(k)

    headers = [x for x in headers + end if x in found]
    return tools.csv.cereal(rows=raw_data, headers=headers)
