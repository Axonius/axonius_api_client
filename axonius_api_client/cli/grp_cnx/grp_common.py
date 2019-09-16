# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import re

import click

from ... import tools
from .. import context


def to_csv(ctx, raw_data, include_settings=True, **kwargs):
    """Pass."""
    rows = []

    simples = ["adapter_name", "node_name", "id", "uuid", "status_raw", "error"]

    for cnx in raw_data:
        if "cnx" in cnx:
            cnx = cnx["cnx"]

        row = {k: cnx[k] for k in simples}
        if include_settings:
            row["settings"] = context.join_tv(cnx["config"])

        rows.append(row)

    return context.dictwriter(rows=rows)


def handle_schema(config, schema, hiddens, prompt_opt, skips):
    """Pass."""
    name = schema["name"]
    required = schema["required"]
    default = schema.get("default", None)

    schema["hide_input"] = hide_input = any([re.search(x, name) for x in hiddens])

    smsg = "\n{s}\n  Configuration item schema:{it}"
    smsg = smsg.format(s="*" * 40, it=context.join_kv(obj=schema, indent=" " * 4))
    click.secho(message=smsg, fg="blue", err=True)

    if config.get(name):
        hasmsg = "\nSkipping item, was provided via '--config {}=...'\n"
        hasmsg = hasmsg.format(name)
        click.secho(message=hasmsg, fg="cyan", err=True)
        raise SkipItem()

    if not required and any([re.search(x, name) for x in skips]):
        skipmsg = "\nSkipping item, was provided via '--skip {}'\n"
        skipmsg = skipmsg.format(name)
        click.secho(message=skipmsg, fg="cyan", err=True)
        raise SkipItem()

    if not required and not prompt_opt:
        skipmsg = "\nSkipping optional item due to --no-prompt-opt\n"
        skipmsg = skipmsg.format(name)
        click.secho(message=skipmsg, fg="cyan", err=True)
        raise SkipItem()

    ptype = determine_type(schema=schema)
    ptext = "\nProvide value for item"
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

    return value


TYPE_MAP = {
    "bool": click.BOOL,
    "integer": click.INT,
    "number": click.INT,
    "file": click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        allow_dash=False,
        path_type=None,
    ),
}


def determine_type(schema):
    """Pass."""
    type_str = schema["type"]
    enum = schema.get("enum", [])
    has_enum = "enum" in schema

    ptype = None

    if type_str == "string" and has_enum and isinstance(enum, tools.LIST) and enum:
        ptype = click.Choice(choices=enum, case_sensitive=True)
    elif type_str in TYPE_MAP:
        ptype = TYPE_MAP[type_str]

    return ptype


class SkipItem(Exception):
    """Pass."""


def handle_response(cnx, action):
    """Pass."""
    had_error = cnx["response_had_error"]
    response = cnx["response"]

    info_keys = ["adapter_name", "node_name", "id", "uuid", "status", "error"]
    cnxinfo = {k: cnx["cnx"][k] for k in info_keys}

    color = "red" if had_error else "green"

    msg = [
        "",
        "Finished {a} connection",
        "Had error: {he}",
        "response:\n{r}",
        "connection:{ci}\n",
    ]
    msg = tools.join_cr(obj=msg, pre=False, indent="").format(
        a=action,
        he=had_error,
        r=tools.json_dump(response),
        ci=context.join_kv(obj=cnxinfo, indent=" " * 2),
    )
    click.secho(message=msg, fg=color, err=True)
