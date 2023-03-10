# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ..context import CONTEXT_SETTINGS, click
from ..grp_tools.grp_common import EXPORT_FORMATS
from ..grp_tools.grp_options import OPT_ENV, OPT_EXPORT
from ..options import AUTH, add_options

OPTIONS = [*AUTH, OPT_EXPORT, OPT_ENV]


@click.command(name="get-api-keys", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, env):
    """Get the API keys for the current user."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.api_keys

    click.secho(EXPORT_FORMATS[export_format](data=data, env=env, url=client.AUTH.http.url))
    ctx.exit(0)
