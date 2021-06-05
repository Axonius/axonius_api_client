# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..grp_system.grp_discover.grp_common import do_wait_discover
from ..options import URL, WRITE_ENV, add_options
from .grp_common import handle_keys

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
START_DISCO = click.option(
    "--start-discover/--no-start-discover",
    "-sd/-nsd",
    "start_discover",
    help="Start a discover and wait for it to finish after signing up",
    is_flag=True,
    default=False,
    required=False,
    show_envvar=True,
    show_default=True,
)

OPTIONS = [URL, PASSWORD, COMPANY, CONTACT, *WRITE_ENV, START_DISCO]


@click.command(name="signup")
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    password,
    company_name,
    contact_email,
    env_file,
    write_env,
    config,
    export_format,
    start_discover,
):
    """Perform the initial signup to an instance."""
    client = ctx.obj.get_client(url=url)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.signup.signup(
            password=password, company_name=company_name, contact_email=contact_email
        )

    handle_keys(
        ctx=ctx,
        url=url,
        data=data,
        write_env=write_env,
        env_file=env_file,
        config=config,
        export_format=export_format,
    )

    if start_discover:
        client = ctx.obj.start_client(url=url, key=data["api_key"], secret=data["api_secret"])
        data = client.dashboard.start()
        click.secho("Started discover")
        do_wait_discover(ctx=ctx, client=client)

    ctx.exit(0)
