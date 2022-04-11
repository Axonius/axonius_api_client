# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_EXPORT_FORMAT, OPT_SET_VALUE_OPT

OPTIONS = [*AUTH, OPT_EXPORT_FORMAT, OPT_SET_VALUE_OPT]


@click.command(name="get", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, value):
    """Get Enforcement Sets."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        if value:
            data = client.enforcements.get_set(value=value)
        else:
            data = client.enforcements.get_sets()

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
