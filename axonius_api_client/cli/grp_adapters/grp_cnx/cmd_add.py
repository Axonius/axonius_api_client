# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, NODE_CNX, SPLIT_CONFIG_OPT, add_options
from .grp_common import ACTIVE, EXPORT, PROMPTS, SAVE_AND_FETCH, add_cnx, prompt_config

OPTIONS = [
    *AUTH,
    EXPORT,
    SAVE_AND_FETCH,
    ACTIVE,
    *NODE_CNX,
    *PROMPTS,
    SPLIT_CONFIG_OPT,
]


@click.command(name="add", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, config, **kwargs):
    """Add a connection from prompts or arguments."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    new_config = dict(config)
    prompt_config(ctx=ctx, client=client, new_config=new_config, **kwargs)
    add_cnx(ctx=ctx, client=client, new_config=new_config, **kwargs)
