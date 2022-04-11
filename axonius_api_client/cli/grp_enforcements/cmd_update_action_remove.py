# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import (
    EXPORT_FORMATS,
    OPT_ACTION_CATEGORY,
    OPT_ACTION_NAME,
    OPT_EXPORT_FORMAT,
    OPT_SET_VALUE_REQ,
)

OPTIONS = [*AUTH, OPT_EXPORT_FORMAT, OPT_ACTION_CATEGORY, OPT_ACTION_NAME, OPT_SET_VALUE_REQ]


@click.command(name="update-action-remove", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Remove an action from a set."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.enforcements.update_action_remove(**kwargs)

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
