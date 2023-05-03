# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..options import add_options
from .grp_common import EXPORT_FORMATS
from .grp_options import OPT_ENV, OPT_EXPORT

URL = click.option(
    "--url",
    "-u",
    "url",
    required=True,
    help="URL of an Axonius instance",
    metavar="URL",
    prompt="URL",
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

OPTIONS = [URL, PASSWORD, COMPANY, CONTACT, OPT_EXPORT, OPT_ENV]


@click.command(name="signup")
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, password, company_name, contact_email, export_format, env):
    """Perform the initial signup to an instance."""
    client = ctx.obj.create_client(url=url)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.signup.signup(
            password=password, company_name=company_name, contact_email=contact_email
        )
    click.secho(EXPORT_FORMATS[export_format](data=data, signup=True, env=env, url=client.http.url))
    ctx.obj.echo_ok("Signup completed successfully!")
    ctx.exit(0)
