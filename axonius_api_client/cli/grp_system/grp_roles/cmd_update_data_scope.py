# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_ROLE_NAME, OPTS_EXPORT

OPT_DATA_SCOPE = click.option(
    "--data-scope",
    "-ds",
    "data_scope",
    help="Name or UUID of Data Scope restriction to apply",
    required=False,
    show_envvar=True,
    show_default=True,
)
OPT_REMOVE = click.option(
    "--remove/--no-remove",
    "-r/-nr",
    "remove",
    help="Remove the data scope from the role (--data-scope value ignored)",
    required=False,
    default=False,
    show_envvar=True,
    show_default=True,
)
OPTIONS = [*AUTH, *OPTS_EXPORT, OPT_ROLE_NAME, OPT_DATA_SCOPE, OPT_REMOVE]


@click.command(name="update-data-scope", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, name, data_scope, remove, **kwargs):
    """Update a roles data scope."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system_roles.update_data_scope(
            name=name, data_scope=data_scope, remove=remove
        )
        data_scope = data["data_scope_name"]
        ctx.obj.echo_ok(f"Updated role {name!r} data scope to {data_scope!r}")

    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
