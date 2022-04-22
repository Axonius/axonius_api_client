# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPTS_EXPORT

OPT_VALUE = click.option(
    "--value",
    "-v",
    "value",
    help="Name or UUID of data scope",
    required=False,
    show_envvar=True,
    show_default=True,
)

OPTIONS = [*AUTH, *OPTS_EXPORT, OPT_VALUE]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, value):
    """Get data scopes."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.data_scopes.get(value=value)

    count = len(data) if isinstance(data, list) else 1
    ctx.obj.echo_ok(f"Fetched {count} data scopes")
    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
