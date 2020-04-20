# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import add_options
from .grp_common import add_handler as handler
from .grp_options import ADD as OPTIONS

METHOD = "add"
EPILOG = """Note:

Creating a saved query using this method will not create a proper set of
expressions, which will mean the query wizard will not show the filter lines
for the supplied query!
"""


@click.command(name=METHOD, context_settings=CONTEXT_SETTINGS, epilog=EPILOG)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Add a saved query."""
    handler(ctx=ctx, url=url, key=key, secret=secret, **kwargs)
