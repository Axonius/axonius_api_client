# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import (
    AUTH,
    EXPORT,
    FIELDS_SELECT,
    PAGING,
    QUERY,
    add_options,
    get_option_fields_default,
    get_option_help,
)
from .grp_common import GET_EXPORT, load_whitelist

OPTIONS = [
    *AUTH,
    *PAGING,
    *EXPORT,
    *GET_EXPORT,
    *FIELDS_SELECT,
    get_option_fields_default(default=True),
    *QUERY,
    get_option_help(choices=["auth", "query", "assetexport", "selectfields"]),
]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, query_file, whitelist=None, **kwargs):
    """Get assets using a query and fields."""
    if query_file:
        kwargs["query"] = query_file.read().strip()

    kwargs["report_software_whitelist"] = load_whitelist(whitelist)

    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        apiobj.get(**kwargs)
