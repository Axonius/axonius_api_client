# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPTS_EXPORT

OPTIONS = [
    *AUTH,
    *OPTS_EXPORT,
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
]


@click.command(name="is-data-stable", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, for_next_minutes, export_format, phases, progress):
    """Return exit code 0 of data is not stable, 1 if it is."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.dashboard.get()

    click.secho(EXPORT_FORMATS[export_format](data=data, phases=phases, progress=progress))
    reason, is_stable = data.get_stability(for_next_minutes=for_next_minutes)
    ctx.obj.echo_ok(f"Data is stable: {is_stable}, reason: {reason}")
    ctx.exit(int(is_stable))
