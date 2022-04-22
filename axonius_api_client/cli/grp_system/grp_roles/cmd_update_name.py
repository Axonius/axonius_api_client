# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_ROLE_NAME, OPTS_EXPORT

OPT_UPDATE = click.option(
    "--new-name",
    "-nn",
    "new_name",
    help="New name of role",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPTIONS = [*AUTH, *OPTS_EXPORT, OPT_ROLE_NAME, OPT_UPDATE]


@click.command(name="update-name", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, name, new_name, **kwargs):
    """Update a roles name."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system_roles.set_name(name=name, new_name=new_name)
        ctx.obj.echo_ok(f"Updated role name from {name!r} to {new_name!r}")

    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
