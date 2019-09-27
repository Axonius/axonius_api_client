# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, click_ext, options, serial
from . import grp_common

# FUTURE: accept ini based conf file?


@click.command(name="add", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
@options.OPT_INCLUDE_SETTINGS
@click.option(
    "--adapter",
    "-a",
    "adapter",
    help="The name of the adapter to add the connection to.",
    required=True,
    show_envvar=True,
)
@click.option(
    "--node",
    "-n",
    "node",
    help="The name of the node running --adapter to add the connection to.",
    default="master",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--config",
    "-c",
    "config",
    help="Configuration keys in the form of key=value.",
    type=click_ext.SplitEquals(),
    multiple=True,
    show_envvar=True,
)
@click.option(
    "--skip",
    "-sk",
    "skips",
    help="Regexes of configuration keys to not prompt for.",
    multiple=True,
    show_envvar=True,
)
@click.option(
    "--hidden",
    "hiddens",
    help="Regexes of configuration keys to hide input of when prompting.",
    default=cli_constants.HIDDEN,
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--no-prompt-opt",
    "-npo",
    "prompt_opt",
    help="Prompt for optional items that are not supplied.",
    is_flag=True,
    default=True,
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
    adapter,
    node,
    config,
    skips,
    hiddens,
    prompt_opt,
    include_settings,
):
    """Add an adapter connection."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        adapter = client.adapters.get_single(adapter=adapter, node=node)

    config = dict(config)
    skips = [x.lower().strip() for x in skips]
    hiddens = [x.lower().strip() for x in hiddens]

    schemas = adapter["cnx_settings"].values()
    schemas = sorted(schemas, key=lambda x: x["required"], reverse=True)

    for schema in schemas:
        try:
            config[schema["name"]] = grp_common.handle_schema(
                ctx=ctx,
                config=config,
                schema=schema,
                hiddens=hiddens,
                prompt_opt=prompt_opt,
                skips=skips,
            )
        except grp_common.SkipItem:
            continue

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        cnx = client.adapters.cnx.add(adapter=adapter, config=config, error=False)

    action = "adding"
    had_error, had_cnx_error = grp_common.handle_response(
        ctx=ctx, cnx=cnx, action=action, cnx_error=True
    )

    formatters = {"json": serial.to_json, "csv": grp_common.to_csv}

    ctx.obj.handle_export(
        raw_data=cnx,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        joiner=export_delim,
        include_settings=include_settings,
    )

    ctx.exit(int(had_error or had_cnx_error))
