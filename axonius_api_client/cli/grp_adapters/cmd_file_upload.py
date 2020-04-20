# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import json_dump
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, CONTENTS, NODE, add_options

OPTIONS = [
    *AUTH,
    *NODE,
    # field_name
    # file_name
    CONTENTS,
]


@click.command(name="file-upload", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, stream, **kwargs):
    """Upload a file to an adapter for later use with a connection."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    stream_name = format(getattr(stream, "name", stream))
    kwargs["file_name"] = stream_name
    kwargs["field_name"] = stream_name
    kwargs["file_content"] = ctx.obj.read_stream(stream=stream)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.adapters.file_upload(**kwargs)

    ctx.obj.echo_ok(f"File uploaded")
    click.echo(json_dump(rows, indent=None))
