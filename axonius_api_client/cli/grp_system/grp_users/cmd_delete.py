# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

USER_NAME = click.option(
    "--name",
    "-n",
    "name",
    help="Name of user",
    required=True,
    show_envvar=True,
    show_default=True,
)


OPTIONS = [*AUTH, USER_NAME]


@click.command(name="delete", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, name, **kwargs):
    """Delete a user."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        client.system_users.delete(name=name)
        ctx.obj.echo_ok(f"Deleted user {name!r}")
