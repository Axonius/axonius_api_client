# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, FIELDS_SELECT, PAGING, SQ_NAME, add_options, get_option_help
from .grp_common import GET_EXPORT, HISTORY, OPTS_EXPORT, OPTS_GET_BY_SQ, load_whitelist

METHOD = "get-by-saved-query"
OPTIONS = [
    *AUTH,
    *PAGING,
    *OPTS_EXPORT,
    *GET_EXPORT,
    *FIELDS_SELECT,
    *HISTORY,
    *OPTS_GET_BY_SQ,
    SQ_NAME,
    get_option_help(choices=["auth", "assetexport", "selectfields", "asset_helper"]),
]


@click.command(name="get-by-saved-query", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, whitelist=None, **kwargs):
    """Get assets using a saved query."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    kwargs["report_software_whitelist"] = load_whitelist(whitelist)
    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        apiobj.get_by_saved_query(**kwargs)
