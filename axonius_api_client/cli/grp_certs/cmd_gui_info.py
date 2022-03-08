# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

OPTIONS = [*AUTH]


@click.command(name="gui-info", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret):
    """Get GUI certificate basic info from the REST API."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = client.settings_global

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.gui_cert_info()

    click.secho(f"{data}")
    ctx.exit(0)
