# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import cli_constants, options
from . import grp_common


@click.command(name="get-by-mac", context_settings=cli_constants.CONTEXT_SETTINGS)
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
@options.OPT_GET_BY_VALUES
@options.OPT_GET_BY_POST_QUERY
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
    values,
    query,
    fields,
    fields_default,
    max_rows,
):
    """Get assets with matching MAC addresses."""
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
        values=values,
        query=query,
        fields=fields,
        fields_default=fields_default,
        max_rows=max_rows,
        method="get_by_mac",
    )
