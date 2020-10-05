# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...parsers.tables import tablize_adapters
from ...tools import json_dump
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

OPTIONS = [
    *AUTH,
    click.option(
        "--export-format",
        "-xf",
        "export_format",
        type=click.Choice(["json-full", "json", "table", "str", "str-args"]),
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
        rows = client.adapters.get(**kwargs)

    if export_format == "json":

        basic_keys = [
            "name",
            "node_name",
            "cnx_count_total",
            "cnx_count_broken",
            "cnx_count_working",
        ]

        basic = []
        for row in rows:
            new_row = {k: row[k] for k in basic_keys}
            new_row["cnx_ids_broken"] = [x["id"] for x in row["cnx"] if not x["working"]]
            new_row["cnx_ids_working"] = [x["id"] for x in row["cnx"] if x["working"]]
            basic.append(new_row)

        click.secho(json_dump(basic))
    elif export_format == "json-full":
        click.secho(json_dump(rows))
    elif export_format == "table":
        click.secho(tablize_adapters(adapters=rows))
    elif export_format == "str-args":
        lines = "\n".join(["--node-name {node_name} --name {name}".format(**row) for row in rows])
        click.secho(lines)
    elif export_format == "str":
        lines = "\n".join(["{node_name}:{name}".format(**row) for row in rows])
        click.secho(lines)
    ctx.exit(0)
