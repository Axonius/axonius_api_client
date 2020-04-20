# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import add_options
from .grp_common import del_handler as handler
from .grp_options import DELETE_BY_TAGS as OPTIONS

METHOD = "delete-by-tags"


@click.command(name=METHOD, context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Delete saved queries by tags."""
    handler(ctx=ctx, url=url, key=key, secret=secret, get_method="get_by_tags", **kwargs)
