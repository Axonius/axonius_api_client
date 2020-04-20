# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import add_options
from .grp_common import file_upload_handler as handler
from .grp_options import FILE_UPLOAD as OPTIONS

METHOD = "file-upload"


@click.command(name=METHOD, context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Upload a file to an adapter for later use with a connection."""
    handler(ctx=ctx, url=url, key=key, secret=secret, **kwargs)
