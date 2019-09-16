# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context
from . import grp_common


@click.command("get-by-ip", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@context.export_options
@grp_common.get_by_opts
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
    value,
    query,
    field,
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
        value=value,
        query=query,
        field=field,
        fields_default=fields_default,
        max_rows=max_rows,
        method="get_by_ip",
    )
