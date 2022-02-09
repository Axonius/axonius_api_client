# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_SLEEP, OPTS_EXPORT, wait_stable

OPTIONS = [
    *AUTH,
    *OPTS_EXPORT,
    click.option(
        "--wait/--no-wait",
        "-w/-nw",
        "wait",
        help="Wait until data is stable before returning",
        is_flag=True,
        default=False,
        show_envvar=True,
        show_default=True,
    ),
    OPT_SLEEP,
]


@click.command(name="start", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, sleep, wait, export_format, phases, progress):
    """Start the discover cycle."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.dashboard.start()
    ctx.obj.echo_ok("Discover cycle started!")
    click.secho(EXPORT_FORMATS[export_format](data=data))
    wait_stable(
        client=client,
        ctx=ctx,
        sleep=sleep,
        wait=wait,
        export_format=export_format,
        phases=phases,
        progress=progress,
    )
    ctx.exit(0)
