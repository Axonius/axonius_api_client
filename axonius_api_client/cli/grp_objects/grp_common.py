# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import functools

import click

from .. import context


def get_by_opts(func):
    """Combine commonly appearing @click.option decorators."""
    #
    @click.option(
        "--value",
        "-v",
        help="Values to search for.",
        required=True,
        multiple=True,
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--query",
        "-q",
        help="Query to add to the end of the query built to search for --value.",
        default="",
        metavar="QUERY",
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--field",
        "-f",
        help="Columns to include in the format of adapter:field.",
        metavar="ADAPTER:FIELD",
        multiple=True,
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--fields-default/--no-fields-default",
        "-fd/-nfd",
        default=True,
        help="Include default columns for this object type.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
    )
    @click.option(
        "--max-rows",
        "-mr",
        help="Only return this many rows.",
        type=click.INT,
        hidden=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def get_by_cmd(
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
    method,
):
    """Pass."""
    client = ctx.start_client(url=url, key=key, secret=secret)

    api = getattr(client, clickctx.parent.command.name)

    apimethod = getattr(api, method)

    with context.exc_wrap(wraperror=ctx.wraperror):
        raw_data = apimethod(
            value=value[0] if context.is_list(value) and len(value) == 1 else value,
            query_post=query,
            fields=field,
            fields_default=fields_default,
            max_rows=max_rows,
        )

    formatters = {"json": context.to_json, "csv": context.obj_to_csv}

    ctx.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
    )
