# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import CONTEXT_SETTINGS
from ..options import URL, add_options
from .grp_common import do_wait_status, get_status

OPTIONS = [
    URL,
    click.option(
        "--wait/--no-wait",
        "-w/-nw",
        "wait",
        help="Wait until system is ready before returning",
        is_flag=True,
        default=False,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--sleep",
        "sleep",
        help="Seconds to wait for each ready check",
        type=click.IntRange(min=0),
        default=30,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--max-wait",
        "max_wait",
        help="Maximum seconds to wait",
        type=click.IntRange(min=1),
        default=60 * 15,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="system-status", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, wait, sleep, max_wait):
    """Get the status of the Axonius instance."""
    client = ctx.obj.get_client(url=url)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        is_ready, status_code = get_status(ctx=ctx, client=client)

    if wait:
        do_wait_status(ctx=ctx, client=client, max_wait=max_wait, sleep=sleep, is_ready=is_ready)

    ctx.exit(status_code)
