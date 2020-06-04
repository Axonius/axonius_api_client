# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, SQ_NAME, add_options, get_option_help
from .grp_common import HISTORY_DATE

OPTIONS = [
    *AUTH,
    SQ_NAME,
    HISTORY_DATE,
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
        raw_data = apiobj.count_by_saved_query(**kwargs)

    click.secho(format(raw_data))
