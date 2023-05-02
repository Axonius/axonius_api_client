# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import CONTEXT_SETTINGS
from ..options import URL, add_options

TOKEN = click.option(
    "--token",
    "-t",
    "token",
    help="Password reset token (can supply token with full URL, but url argument is used)",
    required=True,
    show_envvar=True,
    show_default=True,
)
PASSWORD = click.option(
    "--password",
    "-p",
    "password",
    required=True,
    help="Password to set",
    prompt="Password to set",
    hide_input=True,
    show_envvar=True,
    show_default=True,
)


OPTIONS = [URL, TOKEN, PASSWORD]


@click.command(name="use-password-reset-token", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, token, password):
    """Use a password reset token."""
    client = ctx.obj.create_client(url=url)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        name = client.signup.use_password_reset_token(token=token, password=password)

    ctx.obj.echo_ok(f"Password successfully reset for user {name!r}")
