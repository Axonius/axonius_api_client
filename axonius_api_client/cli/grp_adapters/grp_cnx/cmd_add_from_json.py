# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
# from ....exceptions import CnxAddError
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, INPUT_FILE, NODE_CNX, add_options
from .grp_common import ACTIVE, EXPORT, SAVE_AND_FETCH, add_cnx

OPTIONS = [
    *AUTH,
    EXPORT,
    SAVE_AND_FETCH,
    ACTIVE,
    *NODE_CNX,
    INPUT_FILE,
]


@click.command(name="add-from-json", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, input_file, **kwargs):
    """Add a connection from a JSON file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    new_config = ctx.obj.read_stream_json(stream=input_file, expect=dict)
    add_cnx(ctx=ctx, client=client, new_config=new_config, **kwargs)
