# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import serial

FORMATTERS = {
    "json": serial.to_json,
    "csv": serial.obj_to_csv,
    "table": serial.obj_to_table,
}


def get_by_cmd(
    ctx,
    url,
    key,
    secret,
    export_format,
    export_file,
    export_path,
    export_overwrite,
    export_table_format,
    joiner,
    values,
    value_regex,
    value_not,
    query_pre,
    query_post,
    fields,
    fields_regex,
    fields_default,
    max_rows,
    method,
):
    """Pass."""
    p_grp = ctx.parent.command.name

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    api = getattr(client, p_grp)
    apimethod = getattr(api, method)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        raw_data = apimethod(
            value=values[0] if serial.is_list(values) and len(values) == 1 else values,
            value_regex=value_regex,
            value_not=value_not,
            query_pre=query_pre,
            query_post=query_post,
            fields=fields,
            fields_regex=fields_regex,
            fields_default=fields_default,
            max_rows=max_rows,
        )

    echo_response(ctx=ctx, raw_data=raw_data, api=api)

    ctx.obj.handle_export(
        raw_data=raw_data,
        formatters=FORMATTERS,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
        table_format=export_table_format,
        joiner=joiner,
    )


def echo_response(ctx, raw_data, api):
    """Pass."""
    last_get = getattr(api, "_LAST_GET", {})
    last_filter = last_get.get("filter", "")
    last_fields = "\n  ".join(last_get.get("fields", "").split(","))

    ctx.obj.echo_ok("Returned {} rows".format(len(raw_data)))
    ctx.obj.echo_ok("Query: {!r}".format(last_filter))
    ctx.obj.echo_ok("Fields:\n  {}".format(last_fields))


def get_sources(ctx):
    """Pass."""
    pp_grp = ctx.parent.parent.command.name
    src_cmds = [x for x in ctx.parent.parent.command.commands if x.startswith("get")]
    return ["{pp} {c}".format(pp=pp_grp, c=c) for c in src_cmds]


def show_sources(ctx, param=None, value=None):
    """Pass."""
    if value:
        pp_grp = ctx.parent.parent.command.name
        p_grp = ctx.parent.command.name
        grp = ctx.command.name

        this_grp = "{pp} {p} {g}".format(pp=pp_grp, p=p_grp, g=grp)
        this_cmd = "{tg} --rows".format(tg=this_grp)

        src_cmds = get_sources(ctx=ctx)
        msg = serial.ensure_srcs_msg(this_cmd=this_cmd, src_cmds=src_cmds)
        click.secho(message=msg, err=True, fg="green")
        ctx.exit(0)


def get_rows(ctx, rows):
    """Pass."""
    pp_grp = ctx.parent.parent.command.name
    p_grp = ctx.parent.command.name
    grp = ctx.command.name

    this_grp = "{pp} {p} {g}".format(pp=pp_grp, p=p_grp, g=grp)
    this_cmd = "{tg} --rows".format(tg=this_grp)

    src_cmds = get_sources(ctx=ctx)

    rows = serial.json_to_rows(
        ctx=ctx, stream=rows, this_cmd=this_cmd, src_cmds=src_cmds
    )

    serial.check_rows_type(
        ctx=ctx, rows=rows, this_cmd=this_cmd, src_cmds=src_cmds, all_items=False
    )

    serial.ensure_keys(
        ctx=ctx,
        rows=rows,
        this_cmd=this_cmd,
        src_cmds=src_cmds,
        keys=["internal_axon_id", "adapters"],
        all_items=False,
    )
    return rows
