# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import click

from .. import cli_constants, options
from . import grp_common


@click.command(
    name="get-by-saved-query", context_settings=cli_constants.CONTEXT_SETTINGS
)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
@options.OPT_EXPORT_TABLE_FORMAT
@options.OPT_FIELDS
@options.OPT_FIELDS_REGEX
@options.OPT_MAX_ROWS
@options.OPT_PAGE_START
@options.OPT_PAGE_SIZE
@options.OPT_FIELD_NULLS
@options.OPT_FIELD_EXCLUDES
@click.option(
    "--name",
    "-n",
    help="Name of saved query to get assets from.",
    required=True,
    show_envvar=True,
)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Get assets from a saved query."""
    p_grp = ctx.parent.command.name

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    api = getattr(client, p_grp)

    kwargs["callbacks"] = grp_common.handle_callbacks(**kwargs)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_data = api.get_by_saved_query(**kwargs)

    grp_common.echo_response(ctx=ctx, raw_data=raw_data, api=api)

    kwargs["formatters"] = grp_common.FORMATTERS
    kwargs["raw_data"] = raw_data
    ctx.obj.handle_export(**kwargs)
