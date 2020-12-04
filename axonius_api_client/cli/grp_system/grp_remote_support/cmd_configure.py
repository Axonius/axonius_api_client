# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT, handle_export

OPTIONS = [
    *AUTH,
    *EXPORT,
    click.option(
        "--enable/--disable",
        "-e/-d",
        "enable",
        default=None,
        help="Enable or disable 'Remote Support'",
        is_flag=True,
        multiple=False,
        required=True,
        show_default=True,
        show_envvar=True,
    ),
    click.option(
        "--temp-hours",
        "-th",
        "temp_hours",
        default=None,
        help="When enabling, only enable temporarily for N hours",
        multiple=False,
        required=False,
        show_default=True,
        show_envvar=True,
        type=click.INT,
    ),
]


@click.command(name="configure", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, enable, temp_hours, **kwargs):
    """Update the remote support configuration."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.remote_support.configure(enable=enable, temp_hours=temp_hours)

    handle_export(ctx=ctx, data=data, **kwargs)
