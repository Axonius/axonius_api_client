# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import json_dump
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, NODE, add_options

OPTIONS = [
    *AUTH,
    *NODE,
    click.option(
        "--input-file",
        "-if",
        "input_file",
        help="File to upload (from path or piped via STDIN)",
        default="-",
        type=click.File(mode="r"),
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="file-upload", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, input_file, **kwargs):
    """Upload a file to an adapter for later use with a connection."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    stream_name = format(getattr(input_file, "name", input_file))
    kwargs["file_name"] = stream_name
    kwargs["field_name"] = stream_name
    kwargs["file_content"] = ctx.obj.read_stream(stream=input_file)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.adapters.file_upload(**kwargs)

    ctx.obj.echo_ok("File uploaded")
    click.echo(json_dump(rows, indent=None))
