# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_VALUE, OPTS_EXPORT, OPTS_UPDATE_SCOPE

OPTIONS = [*AUTH, *OPTS_EXPORT, OPT_VALUE, *OPTS_UPDATE_SCOPE]


@click.command(name="update-user-scopes", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, value, update, append, remove):
    """Update the user asset scopes of a data scope."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.data_scopes.update_user_scopes(
            value=value, update=update, append=append, remove=remove
        )

    ctx.obj.echo_ok(f"Successfully updated data scope: {data.name}")
    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
