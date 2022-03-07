# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import CONTEXT_SETTINGS
from ..options import add_options
from .grp_common import OPTS_EXPORT, from_url, handle_export

OPTIONS = [
    click.option(
        "--url",
        "-u",
        "url",
        help="URL of host to get certificate from",
        show_envvar=True,
        show_default=True,
        required=True,
    ),
    *OPTS_EXPORT,
]


@click.command(name="from-url", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, **kwargs):
    """Display/save certificates from a URL."""
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        chain = from_url(url=url, split=False)
        handle_export(data=chain, **kwargs)
    ctx.exit(0)
