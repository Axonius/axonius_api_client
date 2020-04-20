# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...api.parsers.tables import tablize_adapters
from ...tools import json_dump
from ..context import click


def get_handler(ctx, url, key, secret, export_format, **kwargs):
    """Pass."""
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
        lines = "\n".join(
            ["--node-name {node_name} --name {name}".format(**row) for row in rows]
        )
        click.secho(lines)
    elif export_format == "str":
        lines = "\n".join(["{node_name}:{name}".format(**row) for row in rows])
        click.secho(lines)
    ctx.exit(0)


def config_get_handler(ctx, url, key, secret, export_format, **kwargs):
    """Pass."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.adapters.config_get(**kwargs)

    config_export(ctx=ctx, rows=rows, export_format=export_format)


def config_update_handler(ctx, url, key, secret, export_format, config, **kwargs):
    """Pass."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    config = dict(config)
    kwargs["kwargs_config"] = config

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.adapters.config_update(**kwargs)
    ctx.obj.echo_ok(f"Updated adapter with config:\n{json_dump(config)}")
    config_export(ctx=ctx, rows=rows, export_format=export_format)


def config_update_file_handler(ctx, url, key, secret, export_format, stream, **kwargs):
    """Pass."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    contents = ctx.obj.read_stream_json(stream=stream, expect=dict)
    kwargs["kwargs_config"] = contents

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.adapters.config_update(**kwargs)
    ctx.obj.echo_ok(f"Updated adapter with config:\n{json_dump(contents)}")
    config_export(ctx=ctx, rows=rows, export_format=export_format)


def file_upload_handler(ctx, url, key, secret, stream, **kwargs):
    """Pass."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    stream_name = format(getattr(stream, "name", stream))
    kwargs["file_name"] = stream_name
    kwargs["field_name"] = stream_name
    kwargs["file_content"] = ctx.obj.read_stream(stream=stream)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.adapters.file_upload(**kwargs)

    ctx.obj.echo_ok(f"File uploaded")
    click.echo(json_dump(rows, indent=None))


def config_export(ctx, rows, export_format):
    """Pass."""
    if export_format == "json":
        click.secho(json_dump(rows["config"]))
    elif export_format == "json-full":
        click.secho(json_dump(rows))
    ctx.exit(0)
