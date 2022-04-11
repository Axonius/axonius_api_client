# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_EXPORT_FORMAT, OPT_SET_VALUE_REQ, OPT_UPDATE_BOOL

OPTIONS = [*AUTH, OPT_EXPORT_FORMAT, OPT_UPDATE_BOOL, OPT_SET_VALUE_REQ]


@click.command(name="update-only-new-assets", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Update only run against new assets."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.enforcements.update_only_new_assets(**kwargs)

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
