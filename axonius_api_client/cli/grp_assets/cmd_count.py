# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, QUERY, add_options, get_option_help
from .grp_common import HISTORY, OPT_USE_CACHE_ENTRY, OPT_USE_HEAVY_FIELDS_COLLECTION, WIZ, load_wiz

OPTIONS = [
    *AUTH,
    *HISTORY,
    OPT_USE_CACHE_ENTRY,
    OPT_USE_HEAVY_FIELDS_COLLECTION,
    *QUERY,
    *WIZ,
    get_option_help(choices=["auth", "query"]),
]


@click.command(name="count", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, query_file, wizard_content, help_detailed=None, **kwargs):
    """Get the count of assets from a query."""
    kwargs["query"] = query_file.read().strip() if query_file else kwargs.get("query")
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    p_grp = ctx.parent.command.name
    apiobj = getattr(client, p_grp)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        kwargs = load_wiz(apiobj=apiobj, wizard_content=wizard_content, kwargs=kwargs)
        data = apiobj.count(**kwargs)

    click.secho(f"{data}")
    ctx.exit(0)
