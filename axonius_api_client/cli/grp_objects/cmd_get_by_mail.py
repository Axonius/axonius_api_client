# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context
from . import grp_common


@click.command(name="get-by-mail", context_settings=context.CONTEXT_SETTINGS)
@context.OPT_URL
@context.OPT_KEY
@context.OPT_SECRET
@context.OPT_EXPORT_FILE
@context.OPT_EXPORT_PATH
@context.OPT_EXPORT_FORMAT
@context.OPT_EXPORT_OVERWRITE
@context.OPT_QUERY
@context.OPT_FIELDS
@context.OPT_FIELDS_DEFAULT
@context.OPT_MAX_ROWS
@context.OPT_GET_BY_VALUES
@context.OPT_GET_BY_POST_QUERY
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
    values,
    query,
    fields,
    fields_default,
    max_rows,
):
    """Get all objects matching a query."""
    grp_common.get_by_cmd(
        clickctx=clickctx,
        ctx=ctx,
        url=url,
        key=key,
        secret=secret,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        values=values,
        query=query,
        fields=fields,
        fields_default=fields_default,
        max_rows=max_rows,
        method="get_by_mail",
    )
