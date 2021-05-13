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
    "-f",
    "first_name",
    help="First name of user",
    required=False,
    show_envvar=True,
    show_default=True,
)
LAST_NAME = click.option(
    "--last-name",
    "-l",
    "last_name",
    help="Last name of user",
    required=False,
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
ROLE_NAME = click.option(
    "--role-name",
    "-r",
    "role_name",
    help="Role to assign to user",
    required=False,
    show_envvar=True,
    show_default=True,
)
OPTIONS = [*AUTH, EXPORT, FIRST_NAME, LAST_NAME, EMAIL, USER_NAME, PASSWORD, ROLE_NAME]


@click.command(name="update", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    export_format,
    name,
    password,
    first_name,
    last_name,
    email,
    role_name,
    **kwargs,
):
    """Update a user."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    if not any([password, first_name, last_name, email, role_name]):
        ctx.obj.echo_error(
            "Must supply at least one of password, first_name, last_name, email, or role_name"
        )

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        if any([first_name, last_name]):
            data = client.system_users.set_first_last(name=name, first=first_name, last=last_name)
            ctx.obj.echo_ok(f"Updated first and last name of user {name!r}")

        if password:
            data = client.system_users.set_password(name=name, password=password)
            ctx.obj.echo_ok(f"Updated password of user {name!r}")

        if email:
            data = client.system_users.set_email(name=name, email=email)
            ctx.obj.echo_ok(f"Updated email of user {name!r}")

        if role_name:
            data = client.system_users.set_role(name=name, role_name=role_name)
            ctx.obj.echo_ok(f"Updated role of user {name!r}")

    handle_export(ctx=ctx, data=data, export_format=export_format, **kwargs)
