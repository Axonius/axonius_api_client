# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import handle_export_search
from .grp_options import OPTS_SEARCH_COPY

OPTIONS = [*AUTH, *OPTS_SEARCH_COPY]


@click.command(name="search-objects-copy", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    export_format,
    export_file,
    export_overwrite,
    table_format,
    include_details,
    echo,
    **kwargs,
):
    """Search for objects in a folder and make copies of them."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    # get the name of the parent click group
    parent_group_name: str = ctx.parent.command.name

    # get the folders api object for this object type
    apiobj = getattr(client.folders, parent_group_name)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        folder, objs = apiobj.search_objects_copy(echo=echo, **kwargs)

    handle_export_search(
        apiobj=apiobj,
        folder=folder,
        objs=objs,
        export_format=export_format,
        export_file=export_file,
        export_overwrite=export_overwrite,
        table_format=table_format,
        include_details=include_details,
        echo=echo,
    )
    ctx.exit(0)
