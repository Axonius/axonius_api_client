# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import re

import click

from ... import tools
from .. import cli_constants, serial


def to_csv(ctx, raw_data, include_settings=True, joiner="\n", **kwargs):
    """Pass."""
    rows = []

    simples = ["adapter_name", "node_name", "id", "uuid", "status_raw", "error"]

    for cnx in raw_data:
        cnx = cnx["cnx"] if "cnx" in cnx else cnx
        row = {k: cnx[k] for k in simples}
        if include_settings:
            row["settings"] = serial.join_tv(obj=cnx["config"], joiner=joiner)

        rows.append(row)

    return serial.dictwriter(rows=rows)


def fixup_schema(schema, hiddens):
    """Pass."""
    if "enum" in schema:
        schema["valid_choices"] = schema.pop("enum")

    schema["hide_input"] = any([re.search(x, schema["name"]) for x in hiddens])

    schema = {k: schema[k] for k in sorted(schema.keys())}
    return schema


def show_schema(ctx, schema, hiddens, err=True):
    """Pass."""
    smsg = "\n{s}\n  Configuration item schema:{it}"
    smsg = smsg.format(s="*" * 40, it=serial.join_kv(obj=schema, indent=" " * 4))
    click.secho(message=smsg, fg="blue", err=err)


def handle_schema(ctx, config, schema, hiddens, prompt_opt, skips):
    """Pass."""
    name = schema["name"]
    required = schema["required"]
    default = schema.get("default", None)

    show_schema(ctx=ctx, schema=schema, hiddens=hiddens, err=True)
    hide_input = schema["hide_input"]

    if config.get(name):
        hasmsg = "\nSkipping item, was provided via '--config {v!r}=...'\n"
        hasmsg = hasmsg.format(v=name)
        click.secho(message=hasmsg, fg="cyan", err=True)
        raise SkipItem()

    if not required and any([re.search(x, name) for x in skips]):
        skipmsg = "\nSkipping item, was provided via '--skip {v!r}'\n"
        skipmsg = skipmsg.format(v=name)
        click.secho(message=skipmsg, fg="cyan", err=True)
        raise SkipItem()

    if not required and not prompt_opt:
        skipmsg = "\nSkipping optional item {v!r} due to --no-prompt-opt\n"
        skipmsg = skipmsg.format(v=name)
        click.secho(message=skipmsg, fg="cyan", err=True)
        raise SkipItem()

    ptype = determine_type(schema=schema)
    skippable = not required and ptype is None

    ptext = "\nProvide value for item{sk}"
    ptext = ptext.format(sk=" (SKIP to skip)" if skippable else "")
    ptext = click.style(text=ptext, fg="bright_blue")

    value = click.prompt(
        text=ptext,
        default=default,
        hide_input=hide_input,
        type=ptype,
        err=True,
        show_default=True,
        show_choices=True,
    )

    if format(value).upper() == "SKIP":  # pragma: no cover
        skipmsg = "\nSkipping item {v!r} due to value 'SKIP'\n"
        skipmsg = skipmsg.format(v=name)
        click.secho(message=skipmsg, fg="cyan", err=True)
        raise SkipItem()

    return value


def determine_type(schema):
    """Pass."""
    type_str = schema["type"]
    enum = schema.get("enum", [])
    has_enum = "enum" in schema

    ptype = None

    if type_str == "string" and has_enum and isinstance(enum, tools.LIST) and enum:
        ptype = click.Choice(choices=enum, case_sensitive=True)
    elif type_str in cli_constants.SETTING_TYPE_MAP:
        ptype = cli_constants.SETTING_TYPE_MAP[type_str]

    return ptype


class SkipItem(Exception):
    """Pass."""


def handle_response(ctx, cnx, action, cnx_error=True):
    """Pass."""
    had_cnx_error = bool(cnx["cnx"]["error"])
    had_error = cnx["response_had_error"]
    response = cnx["response"]

    info_keys = ["adapter_name", "node_name", "id", "uuid", "status", "error"]
    cnxinfo = {k: cnx["cnx"][k] for k in info_keys}

    color = "red" if had_error or had_cnx_error else "green"

    msg = [
        "\nFINISHED {a} CONNECTION",
        "Had error: {he}",
        "response: {resp}",
        "connection:{ci}\n",
    ]
    msg = tools.join_cr(obj=msg, pre=False, indent="  ").format(
        a=action.upper(),
        he=had_error or (had_cnx_error and cnx_error),
        resp=tools.json_dump(response).strip(),
        ci=serial.join_kv(obj=cnxinfo, indent="   "),
    )
    click.secho(message=msg, fg=color, err=True)

    return had_error, had_cnx_error


def get_sources(ctx):
    """Pass."""
    pp_grp = ctx.parent.parent.command.name
    p_grp = ctx.parent.command.name

    src_cmds = ["{pp} {p} get", "{pp} get"]
    src_cmds = [x.format(pp=pp_grp, p=p_grp) for x in src_cmds]
    return src_cmds


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
        ctx=ctx, rows=rows, this_cmd=this_cmd, src_cmds=src_cmds, all_items=True
    )

    rows = serial.collapse_rows(rows=rows, key="cnx")

    serial.ensure_keys(
        ctx=ctx,
        rows=rows,
        this_cmd=this_cmd,
        src_cmds=src_cmds,
        keys=[
            "adapter_name",
            "adapter_name_raw",
            "config_raw",
            "node_id",
            "node_name",
            "id",
            "uuid",
            "status",
            "error",
        ],
        all_items=True,
    )
    return rows


def check_empty(
    ctx, this_data, prev_data, value_type, value, objtype, known_cb, known_cb_key
):
    """Pass."""
    if value in tools.EMPTY:
        return

    value = tools.join_comma(obj=value, empty=False)

    if not this_data:
        valid = tools.join_cr(obj=known_cb(**{known_cb_key: prev_data}))
        msg = "Valid {objtype}:{valid}\n"
        msg = msg.format(valid=valid, objtype=objtype)
        ctx.obj.echo_error(msg, abort=False)

        msg = "No {objtype} found when searching by {value_type}: {value}"
        msg = msg.format(objtype=objtype, value_type=value_type, value=value)
        ctx.obj.echo_error(msg)

    msg = "Found {cnt} {objtype} by {value_type}: {value}"
    msg = msg.format(
        objtype=objtype, cnt=len(this_data), value_type=value_type, value=value
    )
    ctx.obj.echo_ok(msg)
