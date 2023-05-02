# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import add_options
from .options_get import OPTIONS
from .export_get import handle_export


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx, url, key, secret, export_format, export_file, export_overwrite, explode, schemas, **kwargs
):
    """Get Enforcement Center Tasks matching filters."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.enforcements.tasks.get(**kwargs)

    handle_export(
        ctx=ctx,
        data=data,
        export_format=export_format,
        export_file=export_file,
        export_overwrite=export_overwrite,
        explode=explode,
        schemas=schemas,
        **kwargs
    )
    ctx.exit(0)
