# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import click

from . import context


@click.command("get", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@click.option(
    "--query",
    help="Query built from Query Wizard to filter objects (empty returns all).",
    metavar="QUERY",
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--field",
    help="Field (column) to include in the format of adapter:field.",
    callback=context.cb_fields,
    multiple=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--default-fields/--no-default-fields",
    default=True,
    help="Include default fields for this object type.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--all-generic/--no-all-generic",
    default=False,
    help="Ignore --field and --default-fields and include ALL generic fields.",
    is_flag=True,
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
    field,
    default_fields,
    all_generic,
):
    """Get all objects matching a query."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    api = getattr(client, clickctx.parent.command.name)

    kwargs = {"query": query}

    if all_generic:
        # kwargs["default_fields"] = False
        kwargs["general"] = ["all"]
    else:
        kwargs["default_fields"] = default_fields
        kwargs.update(field)

    try:
        raw_data = api.get(**kwargs)
    except Exception as exc:
        if ctx.wraperror:
            ctx.echo_error(format(exc))
        raise

    formatters = {"json": ctx.to_json, "csv": ctx.to_csv}

    ctx.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
    )

    return ctx
