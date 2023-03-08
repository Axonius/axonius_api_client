# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_options import OPTS_FIND

OPTIONS = [*AUTH, *OPTS_FIND]


@click.command(name="find", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, include_details, include_objects, maximum_depth, **kwargs):
    """Find a folder."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    # get the name of the parent click group
    parent_group_name: str = ctx.parent.command.name

    # get the folders api object for this object type
    apiobj = getattr(client.folders, parent_group_name)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        folder = apiobj.find(**kwargs)
        data = folder.get_tree(
            include_details=include_details,
            include_objects=include_objects,
            maximum_depth=maximum_depth,
            as_str=True,
        )
    click.secho(data)
    click.secho(f"Found Path: {folder.path}")
    ctx.exit(0)
