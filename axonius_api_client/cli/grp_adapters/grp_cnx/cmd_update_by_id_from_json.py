# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import INPUT_FILE, add_options
from .cmd_update_by_id import OPTIONS_SHARED, handle_update

OPTIONS = [
    *OPTIONS_SHARED,
    INPUT_FILE,
]


@click.command(name="update-by-id-from-json", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, input_file, **kwargs):
    """Update a connection from a JSON file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    config = ctx.obj.read_stream_json(stream=input_file, expect=dict)
    handle_update(ctx=ctx, client=client, config=config, **kwargs)
