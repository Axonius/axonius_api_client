# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

OPTIONS = [*AUTH]


@click.command(name="get-fields-default", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Get the default fields (columns) for assets."""
    p_grp = ctx.parent.command.name
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = getattr(client, p_grp)
    content = "\n".join(apiobj.fields_default)
    click.secho(content)
    ctx.exit(0)
