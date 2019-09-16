# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context
from . import grp_common

HIDDEN = ["secret", "key", "password"]


@click.command("add", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--adapter",
    "-a",
    help="The name of the adapter to add the connection to.",
    required=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--node",
    "-n",
    help="The name of the node running --adapter to add the connection to.",
    default="master",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--config",
    "-c",
    help="Configuration keys in the form of key=value.",
    type=context.SplitEquals(),
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--skip",
    "-s",
    "skips",
    help="Configuration keys to not prompt for.",
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--hidden",
    "hiddens",
    help="List of configuration items to hide input when prompting.",
    default=HIDDEN,
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--prompt-opt/--no-prompt-opt",
    "-po/-npo",
    help="Prompt for optional items that are not supplied.",
    is_flag=True,
    default=True,
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
@click.option(
    "--error/--no-error",
    "-e/-ne",
    help="Return the new connection object even if an error happens.",
    default=True,
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
    adapter,
    node,
    config,
    skips,
    hiddens,
    prompt_opt,
    error,
    include_settings,
):
    """Get all adapters with clients that have errors."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    with context.exc_wrap(wraperror=ctx.wraperror):
        adapter = client.adapters.get_single(adapter=adapter, node=node)

    config = dict(config)
    skips = [x.lower().strip() for x in skips]
    hiddens = [x.lower().strip() for x in hiddens]

    schemas = adapter["cnx_settings"].values()
    schemas = sorted(schemas, key=lambda x: x["required"], reverse=True)

    for schema in schemas:
        try:
            config[schema["name"]] = grp_common.handle_schema(
                config=config,
                schema=schema,
                hiddens=hiddens,
                prompt_opt=prompt_opt,
                skips=skips,
            )
        except grp_common.SkipItem:
            continue

    with context.exc_wrap(wraperror=ctx.wraperror):
        cnx = client.adapters.cnx.add(adapter=adapter, config=config, error=error)

    grp_common.handle_response(cnx=cnx, action="adding")

    formatters = {"json": context.to_json, "csv": grp_common.to_csv}

    ctx.handle_export(
        raw_data=cnx,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        include_settings=include_settings,
    )
