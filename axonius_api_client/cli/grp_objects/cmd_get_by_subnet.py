# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, options
from . import grp_common


@click.command(name="get-by-subnet", context_settings=cli_constants.CONTEXT_SETTINGS)
@options.OPT_URL
@options.OPT_KEY
@options.OPT_SECRET
@options.OPT_EXPORT_FILE
@options.OPT_EXPORT_PATH
@options.OPT_EXPORT_FORMAT
@options.OPT_EXPORT_OVERWRITE
@options.OPT_EXPORT_DELIM
@options.OPT_FIELDS
@options.OPT_FIELDS_DEFAULT
@options.OPT_MAX_ROWS
@options.OPT_GET_BY_PRE_QUERY
@options.OPT_GET_BY_POST_QUERY
@options.OPT_GET_BY_VALUE_NOT
@click.option(
    "--value",
    "-v",
    "value",
    help="Value to search for.",
    required=True,
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
    value,
    value_not,
    query_pre,
    query_post,
    fields,
    fields_default,
    max_rows,
):
    """Get assets with in a subnet."""
    grp_common.get_by_cmd(
        ctx=ctx,
        url=url,
        key=key,
        secret=secret,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        joiner=export_delim,
        values=value,
        value_regex=False,
        value_not=value_not,
        query_pre=query_pre,
        query_post=query_post,
        fields=fields,
        fields_default=fields_default,
        max_rows=max_rows,
        method="get_by_subnet",
    )
