# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_DATA_SCOPE, OPT_PERMS, OPT_ROLE_NAME, OPTS_EXPORT

OPTIONS = [*AUTH, *OPTS_EXPORT, OPT_ROLE_NAME, OPT_PERMS, OPT_DATA_SCOPE]


@click.command(name="add", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, name, perms, data_scope, table_format, **kwargs):
    """Add a role."""
    perms = dict(perms)
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system_roles.add(name=name, data_scope=data_scope, **perms)
        ctx.obj.echo_ok(f"Added role {name!r}")

    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
