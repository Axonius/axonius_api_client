# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import dt_parse, json_dump, listify
from ...context import click

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(["json", "str"]),
    help="Format of to export data in",
    default="str",
    show_envvar=True,
    show_default=True,
)


def handle_export(ctx, data, export_format, **kwargs):
    """Get roles."""
    if export_format == "json":
        click.secho(json_dump(data))
        ctx.exit(0)

    if export_format == "str":
        for item in listify(data):
            first_name = item["first_name"]
            last_name = item["last_name"]
            role = item["role_obj"]
            role_name = role["name"]
            source = item["source"]
            user_name = item["user_name"]
            last_login = item.get("last_login")
            password_reset_link = item.get("password_reset_link")
            email_password_link_error = item.get("email_password_link_error")

            if last_login:
                last_login = str(dt_parse(last_login))

            lines = [
                f"Name: {user_name!r}",
                f"Role: {role_name!r}",
                f"Last Login: {last_login!r}",
                f"First Name: {first_name!r}",
                f"Last Name: {last_name!r}",
                f"Source: {source!r}",
            ]
            if password_reset_link:
                lines += [
                    f"Password Reset Link: {password_reset_link}",
                    f"Email Password Reset Link Error: {email_password_link_error}",
                ]

            click.secho(", ".join(lines))
        ctx.exit(0)

    ctx.exit(1)
