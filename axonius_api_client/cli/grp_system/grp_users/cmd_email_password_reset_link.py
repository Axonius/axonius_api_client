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
EMAIL = click.option(
    "--email",
    "-e",
    "email",
    help="Email address of user",
    required=False,
    show_envvar=True,
    show_default=True,
)
OPTIONS = [*AUTH, USER_NAME, EMAIL]


@click.command(name="email-password-reset-link", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, name, email, **kwargs):
    """Send a password reset link to a user."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system_users.email_password_reset_link(name=name, email=email)
        ctx.obj.echo_ok(f"Emailed password reset link for user {name!r} to {data!r}")
