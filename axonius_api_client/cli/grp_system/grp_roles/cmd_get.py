# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT, handle_export

ROLE_NAME = click.option(
    "--name",
    "-n",
    "name",
    help="Name of role to get",
    default=None,
    required=False,
    show_envvar=True,
    show_default=True,
)


OPTIONS = [
    *AUTH,
    EXPORT,
    ROLE_NAME,
]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, name, **kwargs):
    """Get all roles or a specific role."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system.roles.get(name=name)

    handle_export(ctx=ctx, data=data, **kwargs)
