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
    default="",
    required=False,
    show_envvar=True,
    show_default=True,
)
GENERATE_PASSWORD = click.option(
    "--generate-password-link/--no-generate-password-link",
    "-gpl/-ngpl",
    "generate_password_link",
    help="Generate a password reset link for the new user",
    default=False,
    is_flag=True,
    show_envvar=True,
    show_default=True,
    required=False,
)
EMAIL_PASSWORD = click.option(
    "--email-password-link/--no-email-password-link",
    "-epl/-nepl",
    "email_password_link",
    help="Email a password reset link to the new user",
    default=False,
    is_flag=True,
    show_envvar=True,
    show_default=True,
    required=False,
)
ROLE_NAME = click.option(
    "--role-name",
    "-r",
    "role_name",
    help="Role to assign to user",
    required=True,
    show_envvar=True,
    show_default=True,
)
FIRST_NAME = click.option(
    "--first-name",
    "-f",
    "first_name",
    help="First name of user",
    required=False,
    show_envvar=True,
    show_default=True,
    default="",
)
LAST_NAME = click.option(
    "--last-name",
    "-l",
    "last_name",
    help="Last name of user",
    required=False,
    show_envvar=True,
    show_default=True,
    default="",
)
EMAIL = click.option(
    "--email",
    "-e",
    "email",
    help="Email address of user",
    required=False,
    show_envvar=True,
    show_default=True,
    default="",
)

OPTIONS = [
    *AUTH,
    EXPORT,
    FIRST_NAME,
    LAST_NAME,
    EMAIL,
    USER_NAME,
    PASSWORD,
    GENERATE_PASSWORD,
    EMAIL_PASSWORD,
    ROLE_NAME,
]


@click.command(name="add", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, name, **kwargs):
    """Add a user."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system_users.add(name=name, **kwargs)
        ctx.obj.echo_ok(f"Added user {name!r}")

    handle_export(ctx=ctx, data=data, export_format=export_format, **kwargs)
