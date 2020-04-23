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
PASSWORD = click.option(
    "--password",
    "-p",
    "password",
    help="Name of user",
    required=False,
    show_envvar=True,
    show_default=True,
)
FIRST_NAME = click.option(
    "--first-name",
    "-fn",
    "firstname",
    help="First name of user",
    default=None,
    required=False,
    show_envvar=True,
    show_default=True,
)
LAST_NAME = click.option(
    "--last-name",
    "-ln",
    "lastname",
    default=None,
    help="Last name of user",
    required=False,
    show_envvar=True,
    show_default=True,
)

OPTIONS = [*AUTH, EXPORT, FIRST_NAME, LAST_NAME, USER_NAME, PASSWORD]


@click.command(name="update", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, name, **kwargs):
    """Update a user."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system.users.update(name=name, **kwargs)
        ctx.obj.echo_ok(f"Updated user {name!r}")

    handle_export(ctx=ctx, data=data, export_format=export_format, **kwargs)
