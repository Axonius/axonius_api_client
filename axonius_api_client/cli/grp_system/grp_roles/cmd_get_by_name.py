# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT, ROLE_NAME, handle_export

OPTIONS = [
    *AUTH,
    EXPORT,
    ROLE_NAME,
]


@click.command(name="get-by-name", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, name, **kwargs):
    """Get a single role."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system_roles.get_by_name(name=name)

    handle_export(ctx=ctx, data=data, **kwargs)
