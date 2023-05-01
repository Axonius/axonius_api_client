# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPTS_EXPORT

OPTIONS = [*AUTH, *OPTS_EXPORT]


@click.command(name="is-running", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, phases, progress):
    """Return exit code 0 if discovery is running, 1 if it is not."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.dashboard.get()

    click.secho(EXPORT_FORMATS[export_format](data=data, phases=phases, progress=progress))
    ctx.obj.echo_ok(f"Is running: {data.is_running}")
    ctx.exit(int(not data.is_running))
