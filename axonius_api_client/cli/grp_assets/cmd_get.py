# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import click

from .. import cli_constants, options
from . import grp_common


@click.command(name="get", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT_ASSETS
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
@options.OPT_EXPORT_TABLE_FORMAT
@options.OPT_QUERY
@options.OPT_QUERY_FILE
@options.OPT_FIELDS
@options.OPT_FIELDS_REGEX
@options.OPT_FIELDS_DEFAULT
@options.OPT_MAX_ROWS
@options.OPT_PAGE_START
@options.OPT_PAGE_SIZE
@options.OPT_FIELD_NULLS
@options.OPT_FIELD_EXCLUDES
@options.OPT_LOG_FIRST_PAGE
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Get assets from a query."""
    if kwargs.get("query_file"):
        kwargs["query"] = kwargs["query_file"].read().strip()

    p_grp = ctx.parent.command.name

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    api = getattr(client, p_grp)

    kwargs = grp_common.handle_kwargs(**kwargs)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        assets = api.get(**kwargs)
        len(assets)

        finish = kwargs.get("finish", None)
        if callable(finish):
            finish(assets=assets, **kwargs)
