# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import export_json_full

MAP_EXPORT_FORMATS: dict = {
    "json": export_json_full,
}

OPT_EXPORT = click.option(
    "--export-format",
    "-xf",
    "export_format",
    type=click.Choice(list(MAP_EXPORT_FORMATS)),
    help="Format of to export data in",
    default="json",
    show_envvar=True,
    show_default=True,
)

OPTIONS = [
    *AUTH,
    OPT_EXPORT,
]


@click.command(name="get-fetch-history-filters", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format):
    """Get filters for adapter fetch history events."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.adapters.get_fetch_history_filters()

    click.secho(MAP_EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
