# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

RESET = click.option(
    "--approve-not-recoverable-action/--no-approve-not-recoverable-action",
    "-a/-na",
    "reset",
    help="Actually perform the factory reset - ALL SETTINGS/USERS/ASSETS will be wiped out!!",
    is_flag=True,
    required=True,
    default=None,
    show_envvar=True,
    show_default=True,
)

OPTIONS = [
    *AUTH,
    RESET,
]


@click.command(name="factory-reset", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, reset, **kwargs):
    """Reset an instance to a fresh installation state."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.instances.factory_reset(reset=reset)

    click.secho(str(data))
    ctx.exit(0 if data.triggered else 1)
