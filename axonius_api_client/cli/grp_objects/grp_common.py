# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

from .. import context


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
    values,
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
            value=values[0] if context.is_list(values) and len(values) == 1 else values,
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
