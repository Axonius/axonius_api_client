# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT, handle_export

OPTIONS = [
    *AUTH,
    *EXPORT,
    click.option(
        "--analytics/--no-analytics",
        "-a/-na",
        "analytics",
        default=None,
        help="Enable or disable 'Remote Support -> Anonymized Analytics'",
        is_flag=True,
        multiple=False,
        required=True,
        show_default=True,
        show_envvar=True,
        type=bool,
    ),
    click.option(
        "--remote-access/--no-remote-access",
        "-ra/-nra",
        "remote_access",
        default=None,
        help="Enable or disable 'Remote Support -> Remote Access'",
        is_flag=True,
        multiple=False,
        required=True,
        show_default=True,
        show_envvar=True,
        type=bool,
    ),
]


@click.command(name="configure-features", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, analytics, remote_access, **kwargs):
    """Enable/disable remote support features."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.remote_support.configure_features(
            analytics=analytics, remote_access=remote_access
        )

    handle_export(ctx=ctx, data=data, **kwargs)
