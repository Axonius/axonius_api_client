# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_options import OPTS_GET_TREE

OPTIONS = [*AUTH, *OPTS_GET_TREE]


@click.command(name="get-tree", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Get a tree view of all subfolders and their objects."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    # get the name of the parent click group
    parent_group_name: str = ctx.parent.command.name

    # get the folders api object for this object type
    apiobj = getattr(client.folders, parent_group_name)

    kwargs["as_str"] = True
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.get_tree(**kwargs)
    click.secho(data)
    ctx.exit(0)
