# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, OPTS_REQ_FOLDER, add_options
from .grp_common import EXPORT_FORMATS, OPT_EXPORT_FORMAT, OPT_SET_VALUE_REQ, OPTS_UPDATE_QUERY

OPTIONS = [*AUTH, OPT_EXPORT_FORMAT, *OPTS_UPDATE_QUERY, OPT_SET_VALUE_REQ, *OPTS_REQ_FOLDER]


# XXX TEST


@click.command(name="update-path", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, **kwargs):
    """Update the path of a set."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        # XXX THIS DOES NOT EXIST YET
        data = client.enforcements.update_path(**kwargs)

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
