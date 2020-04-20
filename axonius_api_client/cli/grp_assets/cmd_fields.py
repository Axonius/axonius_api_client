# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import add_options
from .grp_common import fields_handler as handler
from .grp_options import FIELDS_GET as OPTIONS

METHOD = "fields"


@click.command(name=METHOD, context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Get the available fields (columns) for assets."""
    handler(ctx=ctx, url=url, key=key, secret=secret, method=METHOD, **kwargs)
