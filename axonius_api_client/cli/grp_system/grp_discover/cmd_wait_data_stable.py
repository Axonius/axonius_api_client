# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import OPT_SLEEP, OPTS_EXPORT, Defaults, wait_stable

OPTIONS = [
    *AUTH,
    *OPTS_EXPORT,
    click.option(
        "--for-next-minutes",
        "-fnm",
        "for_next_minutes",
        help="Consider data stable only if next discover will not run in less than N minutes",
        type=click.INT,
        default=Defaults.for_next_minutes,
        show_envvar=True,
        show_default=True,
    ),
    OPT_SLEEP,
]


@click.command(name="wait-data-stable", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, sleep, for_next_minutes, export_format, phases, progress):
    """Wait until data is stable."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    wait_stable(
        client=client,
        ctx=ctx,
        sleep=sleep,
        wait=True,
        export_format=export_format,
        phases=phases,
        progress=progress,
    )
    ctx.exit(0)
