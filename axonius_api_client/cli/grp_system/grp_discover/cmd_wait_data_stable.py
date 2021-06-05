# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import do_wait_discover

OPTIONS = [
    *AUTH,
    click.option(
        "--for-next-minutes",
        "-fnm",
        "for_next_minutes",
        help="Consider data stable only if next discover will not run in less than N minutes",
        type=click.INT,
        default=None,
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--sleep",
        "sleep",
        help="Seconds to wait for each stability check",
        type=click.INT,
        default=60,
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="wait-data-stable", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, sleep, for_next_minutes, **kwargs):
    """Wait until data is stable."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    do_wait_discover(ctx=ctx, client=client, sleep=sleep, for_next_minutes=for_next_minutes)
    ctx.exit(0)
