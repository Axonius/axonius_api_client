# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPTS_EXPORT

OPT_NAME = click.option(
    "--name",
    "-n",
    "name",
    help="Name of data scope",
    required=True,
    show_envvar=True,
    show_default=True,
)
OPT_DESCRIPTION = click.option(
    "--description",
    "-d",
    "description",
    default="",
    help="Description of data scope",
    required=False,
    show_envvar=True,
    show_default=True,
)
OPT_DEVICE_SCOPES = click.option(
    "--device-scope",
    "-ds",
    "device_scopes",
    help="Name or UUID of a Device Asset Scope (multiple)",
    multiple=True,
    required=False,
    show_envvar=True,
    show_default=True,
)
OPT_USER_SCOPES = click.option(
    "--user-scope",
    "-us",
    "user_scopes",
    help="Name or UUID of a User Asset Scope (multiple)",
    multiple=True,
    required=False,
    show_envvar=True,
    show_default=True,
)

OPTIONS = [*AUTH, *OPTS_EXPORT, OPT_NAME, OPT_DESCRIPTION, OPT_DEVICE_SCOPES, OPT_USER_SCOPES]


@click.command(name="create", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    export_format,
    table_format,
    name,
    description,
    device_scopes,
    user_scopes,
):
    """Create a data scope."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.data_scopes.create(
            name=name, description=description, device_scopes=device_scopes, user_scopes=user_scopes
        )

    ctx.obj.echo_ok(f"Successfully created data scope: {data.name}")
    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
