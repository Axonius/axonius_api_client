# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import csv

from .. import tools
from . import cli_constants


def ensure_keys(ctx, rows, this_cmd, src_cmds, keys, all_items=True):
    """Pass."""
    for idx, row in enumerate(rows):
        for key in keys:
            if key not in row:
                ensure_srcs(ctx=ctx, this_cmd=this_cmd, src_cmds=src_cmds)

                msg = [
                    "",
                    "Item #{i} in input to {tc!r} is missing key {k!r}",
                    "Item has keys: {hks}",
                    "Item must have keys: {ks}",
                    "",
                ]
                msg = tools.join_cr(obj=msg).format(
                    i=idx + 1, tc=this_cmd, k=key, ks=keys, hks=list(row)
                )
                ctx.obj.echo_error(msg=msg, abort=True)

        if not all_items:
            break


def ensure_srcs_msg(this_cmd, src_cmds):
    """Pass."""
    psrc = "The input for {tc!r} must be the JSON output from one of these commands:"
    srcs = ["", psrc.format(tc=this_cmd), ""] + src_cmds + [""]
    return tools.join_cr(obj=srcs)


def ensure_srcs(ctx, this_cmd, src_cmds, err=True):
    """Pass."""
    msg = ensure_srcs_msg(this_cmd=this_cmd, src_cmds=src_cmds)
    echo = ctx.obj.echo_error if err else ctx.obj.echo_ok
    echo(msg=msg, abort=False)


def check_rows_type(ctx, rows, this_cmd, src_cmds, all_items=True):
    """Pass."""
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            ensure_srcs(ctx=ctx, this_cmd=this_cmd, src_cmds=src_cmds)

            msg = "Item #{i} in input to {tc!r} is type {t}, must be a dictionary!"
            msg = msg.format(i=idx + 1, tc=this_cmd, t=type(row).__name__)
            ctx.obj.echo_error(msg=msg, abort=True)

        if not all_items:
            break


def json_to_rows(ctx, stream, this_cmd, src_cmds):
    """Pass."""
    stream_name = format(getattr(stream, "name", stream))

    if stream.isatty():
        # its STDIN with no input
        ensure_srcs(ctx=ctx, this_cmd=this_cmd, src_cmds=src_cmds)

        msg = "No input provided on {s!r} for {tc!r}"
        msg = msg.format(s=stream_name, tc=this_cmd)
        ctx.obj.echo_error(msg=msg, abort=True)

    # its STDIN with input or a file
    content = stream.read()
    msg = "Read {n} bytes from {s!r} for {tc!r}"
    msg = msg.format(n=len(content), s=stream_name, tc=this_cmd)
    ctx.obj.echo_ok(msg=msg)

    content = content.strip()

    if not content:
        ensure_srcs(ctx=ctx, this_cmd=this_cmd, src_cmds=src_cmds)

        msg = "Empty content supplied in {s!r} for {tc!r}"
        msg = msg.format(s=stream_name, tc=this_cmd)
        ctx.obj.echo_error(msg=msg, abort=True)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = tools.json_load(obj=content)

    msg = "Loaded JSON rows as {t} with length of {n} for {tc!r}"
    msg = msg.format(t=type(rows).__name__, tc=this_cmd, n=len(rows))
    ctx.obj.echo_ok(msg=msg)

    return tools.listify(obj=rows, dictkeys=False)


def collapse_rows(rows, key):
    """Pass."""
    new_rows = []
    for row in rows:
        if key in row:
            new_rows += tools.listify(obj=row[key], dictkeys=False)
        else:
            new_rows.append(row)
    return new_rows


def join_kv(obj, indent="  ", joiner="\n"):
    """Pass."""
    items = [cli_constants.KV_TMPL.format(k=k, v=v) for k, v in obj.items()]
    return tools.join_cr(obj=items, indent=indent, joiner=joiner)


def join_tv(obj, joiner="\n"):
    """Pass."""
    items = [
        cli_constants.KV_TMPL.format(k=v["title"], v=v["value"]) for k, v in obj.items()
    ]
    return join_cr(obj=items, joiner=joiner)


def join_cr(obj, is_cell=False, joiner="\n"):
    """Pass."""
    str_obj = tools.join_cr(obj=obj, pre=False, post=False, indent="", joiner=joiner)
    max_len = cli_constants.MAX_LEN

    if is_cell and len(str_obj) >= max_len:
        max_str = cli_constants.MAX_STR.format(c=len(obj), mc=max_len)
        str_obj = [str_obj[:max_len], max_str]
        str_obj = tools.join_cr(obj=str_obj)

    return str_obj


def dictwriter(rows, stream=None, headers=None, quoting=cli_constants.QUOTING, **kwargs):
    """Pass."""
    fh = stream or tools.six.StringIO()

    headers = headers or []

    if not headers:
        for row in rows:
            headers += [k for k in row if k not in headers]

    writer = csv.DictWriter(fh, fieldnames=headers, quoting=quoting, **kwargs)

    writer.writeheader()

    for row in rows:
        writer.writerow(row)

    return fh.getvalue()


def to_json(ctx, raw_data, **kwargs):
    """Pass."""
    return tools.json_dump(obj=raw_data)


def is_simple(o):
    """Is simple."""
    return isinstance(o, tools.SIMPLE) or o is None


def is_list(o):
    """Is simple."""
    return isinstance(o, tools.LIST)


def is_los(o):
    """Is simple or list of simples."""
    return is_simple(o) or (is_list(o) and all([is_simple(x) for x in o]))


def is_dos(o):
    """Is dict with simple or list of simple values."""
    return isinstance(o, dict) and all([is_los(v) for v in o.values()])


def obj_to_csv(ctx, raw_data, joiner="\n", **kwargs):
    """Pass."""
    raw_data = tools.listify(obj=raw_data, dictkeys=False)
    rows = []

    for raw_row in raw_data:
        row = {}
        rows.append(row)
        for raw_key, raw_value in raw_row.items():

            if is_los(raw_value):
                row[raw_key] = join_cr(raw_value, is_cell=True, joiner=joiner)
                continue

            if is_list(raw_value) and all([is_dos(x) for x in raw_value]):
                values = {}

                for raw_item in raw_value:
                    for k, v in raw_item.items():
                        new_key = "{}.{}".format(raw_key, k)

                        values[new_key] = values.get(new_key, [])

                        values[new_key] += tools.listify(v, dictkeys=False)

                for k, v in values.items():
                    row[k] = join_cr(v, is_cell=True, joiner=joiner)

                continue

            msg = "Data of type {t} is too complex for CSV format"
            msg = msg.format(t=type(raw_value).__name__)
            row[raw_key] = msg

    return dictwriter(rows=rows)
