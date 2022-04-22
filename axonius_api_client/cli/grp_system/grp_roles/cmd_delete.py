# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_ROLE_NAME, OPTS_EXPORT

OPTIONS = [*AUTH, *OPTS_EXPORT, OPT_ROLE_NAME]


@click.command(name="delete", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, name, export_format, table_format, **kwargs):
    """Delete a role."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system_roles.delete_by_name(name=name)
        ctx.obj.echo_ok(f"Deleted role {name!r}")

    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
