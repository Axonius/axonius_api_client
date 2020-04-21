# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, NODE, add_options
from .grp_common import CONFIG_EXPORT, CONFIG_TYPE, config_export

OPTIONS = [
    *AUTH,
    CONFIG_EXPORT,
    CONFIG_TYPE,
    *NODE,
]


@click.command(name="config-get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Get adapter advanced settings."""
    """Pass."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.adapters.config_get(**kwargs)

    config_export(ctx=ctx, rows=rows, export_format=export_format)
