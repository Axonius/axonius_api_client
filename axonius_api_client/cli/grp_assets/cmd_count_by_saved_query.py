# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, SQ_NAME, add_options, get_option_help
from .grp_common import HISTORY, OPT_USE_CACHE_ENTRY, OPT_USE_HEAVY_FIELDS_COLLECTION

OPTIONS = [
    *AUTH,
    *HISTORY,
    OPT_USE_CACHE_ENTRY,
    OPT_USE_HEAVY_FIELDS_COLLECTION,
    SQ_NAME,
    get_option_help(choices=["auth"]),
]


@click.command(name="count-by-saved-query", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, help_detailed=None, **kwargs):
    """Get the count of assets from a saved query."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = apiobj.count_by_saved_query(**kwargs)

    click.secho(f"{data}")
    ctx.exit(0)
