# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_PERMS, OPT_ROLE_NAME, OPTS_EXPORT

OPT_GRANT = click.option(
    "--allow/--deny",
    "-a/-d",
    "grant",
    help="Permissions supplied should be granted or denied",
    required=False,
    default=True,
    show_envvar=True,
    show_default=True,
)


OPTIONS = [*AUTH, *OPTS_EXPORT, OPT_ROLE_NAME, OPT_PERMS, OPT_GRANT]


@click.command(name="update-perms", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, name, grant, perms, **kwargs):
    """Update a roles permissions."""
    perms = dict(perms)
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system_roles.set_perms(name=name, grant=grant, **perms)
        ctx.obj.echo_ok(f"Updated role permissions for {name!r}")

    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
