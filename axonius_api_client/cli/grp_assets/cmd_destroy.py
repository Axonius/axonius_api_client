# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import json_dump
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

DESTROY = click.option(
    "--destroy/--no-destroy",
    "-d/-nd",
    "destroy",
    help="Actually perform the destroy operation",
    default=None,
    is_flag=True,
    show_envvar=True,
    show_default=True,
    required=True,
)
HISTORY = click.option(
    "--history/--no-history",
    "-h/-nh",
    "history",
    help="Also delete all historical asset records",
    default=None,
    is_flag=True,
    show_envvar=True,
    show_default=True,
    required=True,
)
OPTIONS = [
    *AUTH,
    DESTROY,
    HISTORY,
]


@click.command(name="destroy", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Delete ALL asset records of this type from the database."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.destroy(**kwargs)
    click.secho(json_dump(data))  # pragma: no cover
    ctx.exit(0)  # pragma: no cover
