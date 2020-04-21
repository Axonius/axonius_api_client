# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT, handle_export

USER_NAME = click.option(
    "--name",
    "-n",
    "name",
    help="Name of user",
    required=True,
    show_envvar=True,
    show_default=True,
)
ROLE_NAME = click.option(
    "--role-name",
    "-rn",
    "rolename",
    help="Name of role",
    required=True,
    show_envvar=True,
    show_default=True,
)
OPTIONS = [*AUTH, EXPORT, USER_NAME, ROLE_NAME]


@click.command(name="update-role", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, name, rolename, **kwargs):
    """Update a users role."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system.users.update_role(name=name, rolename=rolename)
        ctx.obj.echo_ok(f"Updated user {name!r} to new role {rolename!r}")

    handle_export(ctx=ctx, data=data, export_format=export_format, **kwargs)
