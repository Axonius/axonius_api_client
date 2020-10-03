# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...api import Signup
from ...tools import json_dump
from ..options import URL, add_options

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
PASSWORD = click.option(
    "--password",
    "-p",
    "password",
    required=True,
    help="Password to assign to admin user",
    prompt="Password to assign to admin user",
    hide_input=True,
    show_envvar=True,
    show_default=True,
)

COMPANY = click.option(
    "--company-name",
    "-cn",
    "company_name",
    required=True,
    help="Company Name",
    prompt="Company Name",
    show_envvar=True,
    show_default=True,
)

CONTACT = click.option(
    "--contact-email",
    "-ce",
    "contact_email",
    required=True,
    help="Contact Email",
    prompt="Contact Email",
    show_envvar=True,
    show_default=True,
)

OPTIONS = [URL, PASSWORD, COMPANY, CONTACT, EXPORT]


@click.command(name="signup")
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, password, company_name, contact_email, export_format):
    """Perform the initial signup to an instance."""
    entry = Signup(url=url)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = entry.signup(
            password=password, company_name=company_name, contact_email=contact_email
        )

    if export_format == "str":
        lines = [
            f"AX_URL={url}",
            f"AX_KEY={data['api_key']}",
            f"AX_SECRET={data['api_secret']}",
        ]
        click.secho("\n".join(lines))
        ctx.exit(0)

    if export_format == "json":
        data["url"] = url
        click.secho(json_dump(data))

    ctx.exit(1)
