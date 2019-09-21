# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

from .. import serial


def get_by_cmd(
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
            query_post=query,
            fields=fields,
            fields_default=fields_default,
            max_rows=max_rows,
        )

    formatters = {"json": serial.to_json, "csv": serial.obj_to_csv}

    ctx.obj.handle_export(
        raw_data=raw_data,
        formatters=formatters,
        export_format=export_format,
        export_file=export_file,
        export_path=export_path,
        export_overwrite=export_overwrite,
    )


def get_rows(ctx, rows):
    """Pass."""
    pp_grp = ctx.parent.parent.command.name
    p_grp = ctx.parent.command.name
    grp = ctx.command.name

    this_grp = "{pp} {p} {g}".format(pp=pp_grp, p=p_grp, g=grp)
    this_cmd = "{tg} --rows".format(tg=this_grp)

    # clickctx.parent.parent.command.commands
    src_cmds = [x for x in ctx.parent.parent.command.commands if x.startswith("get")]
    src_cmds = ["{pp} {c}".format(pp=pp_grp, c=c) for c in src_cmds]
    # src_cmds = serial.ensure_srcs(ctx=ctx, this_cmd=this_cmd, src_cmds=src_cmds)

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
