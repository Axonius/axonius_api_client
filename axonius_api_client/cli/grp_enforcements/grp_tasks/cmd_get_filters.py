# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ...context import CONTEXT_SETTINGS, click
from ...options import add_options
from .export_get_filters import handle_export
from .options_get_filters import OPTIONS


@click.command(name="get-filters", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, export_file, export_overwrite, **kwargs):
    """Get valid values for filtering count or get of Enforcement Center Tasks."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.enforcements.tasks.get_filters()

    handle_export(
        ctx=ctx,
        data=data,
        export_format=export_format,
        export_file=export_file,
        export_overwrite=export_overwrite,
        **kwargs
    )
    ctx.exit(0)
