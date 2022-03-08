# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

OPTIONS = [
    *AUTH,
]


@click.command(name="ca-show", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret):
    """Show the current CA Certificates."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = client.settings_global

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.ca_get()
        click.secho("\n".join(apiobj.cas_to_str(config=data)))
    ctx.exit(0)
