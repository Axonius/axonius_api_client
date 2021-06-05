# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import get_stability

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
]


@click.command(name="is-data-stable", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, for_next_minutes, **kwargs):
    """Return exit code 1 if asset data is stable, 0 if not."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.dashboard.get()

    reason, is_stable = get_stability(data=data, for_next_minutes=for_next_minutes)

    click.secho(f"Data is stable: {is_stable}, reason: {reason}")
    ctx.exit(0 if is_stable else 1)
