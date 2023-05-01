# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ..context import CONTEXT_SETTINGS, click
from ..options import (
    AUTH,
    FIELDS_SELECT,
    PAGING,
    QUERY,
    add_options,
    get_option_fields_default,
    get_option_help,
)
from .grp_common import GET_EXPORT, HISTORY, OPTS_EXPORT, WIZ, load_whitelist, load_wiz

OPTIONS = [
    *AUTH,
    *PAGING,
    *OPTS_EXPORT,
    *GET_EXPORT,
    *FIELDS_SELECT,
    get_option_fields_default(default=True),
    *HISTORY,
    *QUERY,
    *WIZ,
    get_option_help(
        choices=["auth", "query", "assetexport", "selectfields", "wizard", "asset_helper"]
    ),
]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, query_file, wizard_content, whitelist=None, **kwargs):
    """Get assets using a query and fields."""
    kwargs["query"] = query_file.read().strip() if query_file else kwargs.get("query")
    kwargs["report_software_whitelist"] = load_whitelist(whitelist)
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        kwargs = load_wiz(apiobj=apiobj, wizard_content=wizard_content, kwargs=kwargs)
        apiobj.get(**kwargs)
