# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...api import Signup
from ..context import CONTEXT_SETTINGS
from ..options import URL, add_options

OPTIONS = [URL]


@click.command(name="system-status", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url):
    """Get the status of the Axonius instance."""
    entry = Signup(url=url)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = entry.system_status

    click.secho(str(data))
    ctx.exit(data.status_code)
