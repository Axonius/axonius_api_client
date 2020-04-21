# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

# from .grp_common import EXPORT

OPTIONS = [
    *AUTH,
    # EXPORT,
]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Get the current lifecycle information."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.system.discover.lifecycle()

    # json
    click.secho(json_dump(rows))
    # str
    """
    print(
        datetime.datetime.now()
        + datetime.timedelta(seconds=int(system.discover.lifecycle()["next_run_time"]))
    )
    """
