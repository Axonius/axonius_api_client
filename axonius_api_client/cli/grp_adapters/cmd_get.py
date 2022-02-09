# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...parsers.tables import tablize_adapters
from ...tools import json_dump
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options


def export_json_full(data, **kwargs):
    """Pass."""
    return json_dump(data)


def export_json(data, **kwargs):
    """Pass."""
    basic_keys = [
        "name",
        "node_name",
        "cnx_count_total",
        "cnx_count_broken",
        "cnx_count_working",
    ]

    basic = []
    for row in data:
        new_row = {k: row[k] for k in basic_keys}
        new_row["cnx_ids_broken"] = [x["id"] for x in row["cnx"] if not x["working"]]
        new_row["cnx_ids_working"] = [x["id"] for x in row["cnx"] if x["working"]]
        basic.append(new_row)

    return json_dump(basic)


def export_table(data, **kwargs):
    """Pass."""
    return tablize_adapters(adapters=data)


def export_str(data, **kwargs):
    """Pass."""
    return "\n".join(["{node_name}:{name}".format(**x) for x in data])


def export_str_args(data, **kwargs):
    """Pass."""
    return "\n".join(["--node-name {node_name} --name {name}".format(**x) for x in data])


EXPORT_FORMATS: dict = {
    "json": export_json,
    "json-full": export_json_full,
    "table": export_table,
    "str": export_str,
    "str-args": export_str_args,
}

OPTIONS = [
    *AUTH,
    click.option(
        "--export-format",
        "-xf",
        "export_format",
        type=click.Choice(list(EXPORT_FORMATS)),
        help="Format of to export data in",
        default="str",
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get adapter information."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.adapters.get(**kwargs)

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
