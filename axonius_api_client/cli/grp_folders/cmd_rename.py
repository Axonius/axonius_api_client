# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_options import OPTS_RENAME

OPTIONS = [*AUTH, *OPTS_RENAME]


@click.command(name="rename", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Rename a folder."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    # get the name of the parent click group
    parent_group_name: str = ctx.parent.command.name

    # get the folders api object for this object type
    apiobj = getattr(client.folders, parent_group_name)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        folder = apiobj.rename(**kwargs)
    click.secho(f"{folder}")
    click.secho(f"Renamed Path: {folder.path}")
    ctx.exit(0)
