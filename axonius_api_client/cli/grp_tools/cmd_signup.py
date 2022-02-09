# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import datetime

import click

from ...api import Signup
from ...tools import json_dump
from ..options import URL, add_options


def export_str(data):
    """Pass."""
    date = datetime.datetime.utcnow()
    lines = [
        f"AX_URL={data['url']}",
        f"AX_KEY={data['api_key']}",
        f"AX_SECRET={data['api_secret']}",
        f"AX_BANNER=signup on {date}",
    ]
    return "\n".join(lines)


def export_json(data):
    """Pass."""
    return json_dump(data)


EXPORT_FORMATS: dict = {
    "json": export_json,
    "str": export_str,
}

EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(list(EXPORT_FORMATS)),
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
        data["url"] = url

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
