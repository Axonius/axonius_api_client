# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import add_options
from .grp_common import add_handler as handler
from .grp_options import ADD as OPTIONS

METHOD = "add"


@click.command(name=METHOD, context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Add a connection to an adapter."""
    handler(ctx=ctx, url=url, key=key, secret=secret, **kwargs)
