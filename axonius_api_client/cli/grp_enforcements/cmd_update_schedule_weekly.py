# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import (
    EXPORT_FORMATS,
    OPT_EXPORT_FORMAT,
    OPT_RECURRENCE_WEEKLY,
    OPT_SET_VALUE_REQ,
    OPTS_SCHEDULE_TIME,
)

OPTIONS = [*AUTH, OPT_EXPORT_FORMAT, OPT_RECURRENCE_WEEKLY, *OPTS_SCHEDULE_TIME, OPT_SET_VALUE_REQ]


@click.command(name="update-schedule-weekly", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Update a set to run weekly."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.enforcements.update_schedule_weekly(**kwargs)

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
