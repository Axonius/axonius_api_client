# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import ROLE_NAME

OPTIONS = [*AUTH, ROLE_NAME]


@click.command(name="delete", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, name, **kwargs):
    """Delete a role."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        client.system_roles.delete(name=name)
        ctx.obj.echo_ok(f"Deleted role {name!r}")
