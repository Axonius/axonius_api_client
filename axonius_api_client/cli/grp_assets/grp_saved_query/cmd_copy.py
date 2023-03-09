# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...grp_folders.grp_options import OPTS_OBJECT_CREATE
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPTS_EXPORT

OPTIONS = [
    *AUTH,
    *OPTS_EXPORT,
    click.option(
        "--saved-query",
        "-sq",
        "sq",
        help="Name or UUID of saved query to copy",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--name",
        "-n",
        "name",
        help="Name to use for copy",
        required=True,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--private/--no-private",
        "-pr/-npr",
        "private",
        default=False,
        help="Set the copy as private.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        required=False,
    ),
    click.option(
        "--always-cached/--no-always-cached",
        "-ac/-nac",
        "always_cached",
        default=False,
        help="Set the copy as always cached.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        required=False,
    ),
    click.option(
        "--asset-scope/--no-asset-scope",
        "-as/-nas",
        "asset_scope",
        default=False,
        help="Set the copy as an asset scope query.",
        is_flag=True,
        show_envvar=True,
        show_default=True,
        required=False,
    ),
    *OPTS_OBJECT_CREATE,
]


@click.command(name="copy", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, table_format, sq, **kwargs):
    """Copy a Saved Query."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.saved_query.copy(sq=sq, as_dataclass=True, **kwargs)
        ctx.obj.echo_ok(f"Successfully copied Saved Query {sq!r} to {data.name!r}")

    click.secho(EXPORT_FORMATS[export_format](data=data, table_format=table_format))
    ctx.exit(0)
