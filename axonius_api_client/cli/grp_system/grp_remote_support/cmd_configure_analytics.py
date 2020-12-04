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
        help="Enable or disable 'Remote Support > Anonymized Analytics'",
        is_flag=True,
        multiple=False,
        required=True,
        show_default=True,
        show_envvar=True,
    ),
]


@click.command(name="configure-analytics", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, enable, **kwargs):
    """Enable/disable Remote Support > Anonymized Analytics."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.remote_support.configure_analytics(enable=enable)

    handle_export(ctx=ctx, data=data, **kwargs)
