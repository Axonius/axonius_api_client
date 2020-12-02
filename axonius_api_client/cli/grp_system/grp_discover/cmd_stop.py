# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT, handle_export

OPTIONS = [
    *AUTH,
    *EXPORT,
]


@click.command(name="stop", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Stop the discover cycle."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.dashboard.stop()

    handle_export(ctx=ctx, data=data, **kwargs)
