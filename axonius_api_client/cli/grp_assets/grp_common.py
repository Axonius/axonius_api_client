# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import click
import tabulate

from ... import api, tools
from .. import cli_constants, context, serial

FORMATTERS = {
    "json": serial.to_json,
    "csv": serial.obj_to_csv,
    "table": serial.obj_to_table,
}


def get_by_cmd(ctx, url, key, secret, method, values, **kwargs):
    """Pass."""
    p_grp = ctx.parent.command.name

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    api = getattr(client, p_grp)
    apimethod = getattr(api, method)

    kwargs = handle_kwargs(**kwargs)

    get_first = serial.is_list(values) and len(values) == 1
    kwargs["value"] = values[0] if get_first else values

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        apimethod(**kwargs)


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


def assets_to_table(assets, **kwargs):
    """Pass."""
    tablfmt = kwargs.get("export_table_format", cli_constants.EXPORT_TABLE_FORMAT)
    data = tabulate.tabulate(
        tabular_data=assets, tablefmt=tablfmt, showindex=False, headers="keys"
    )
    print(data)
    return data


def handle_kwargs(**kwargs):
    """Pass."""
    kwargs["callbacks"] = []
    kwargs["finish"] = None

    if kwargs.get("query_file"):
        kwargs["query"] = kwargs["query_file"].read().strip()

    if kwargs.get("log_first_page", True):
        kwargs["callbacks"].append(api.assets.cb_firstpage)

    if kwargs.get("field_nulls", False):
        kwargs["callbacks"].append(api.assets.cb_nulls)

    if kwargs.get("field_excludes", []):
        kwargs["callbacks"].append(api.assets.cb_excludes)

    if kwargs.get("field_flatten", False):
        kwargs["callbacks"].append(api.assets.cb_flatten)

    if kwargs.get("field_join", False):
        kwargs["callbacks"].append(api.assets.cb_joiner)

    export_format = kwargs.get("export_format", "")

    if export_format == "json":
        kwargs["callbacks"].append(api.assets.cb_jsonstream)
    elif export_format == "table":
        kwargs["export_table_format"] = tablefmt = kwargs.get(
            "export_table_format", cli_constants.EXPORT_TABLE_FORMAT
        )

        if tablefmt not in tabulate.tabulate_formats:
            tablefmts = tools.join_comma(obj=tabulate.tabulate_formats)
            msg = "{tf!r} is not a valid table format, must be one of {tfs}"
            msg = msg.format(tf=tablefmt, tfs=tablefmts)
            context.click_echo_error(msg=msg, abort=True)

        if api.assets.cb_nulls not in kwargs["callbacks"]:
            kwargs["callbacks"].append(api.assets.cb_nulls)

        if api.assets.cb_flatten not in kwargs["callbacks"]:
            kwargs["callbacks"].append(api.assets.cb_flatten)

        if api.assets.cb_joiner not in kwargs["callbacks"]:
            kwargs["callbacks"].append(api.assets.cb_joiner)

        kwargs["finish"] = assets_to_table

    return kwargs
