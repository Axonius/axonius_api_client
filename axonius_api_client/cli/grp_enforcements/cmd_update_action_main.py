# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""

from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_EXPORT_FORMAT, OPT_SET_VALUE_REQ, OPTS_ACTION_ADD

OPTIONS = [*AUTH, OPT_EXPORT_FORMAT, *OPTS_ACTION_ADD, OPT_SET_VALUE_REQ]


@click.command(name="update-action-main", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, config, **kwargs):
    """Update the main action of a set."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    kwargs["config"] = ctx.obj.read_stream_json(stream=config, expect=dict)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.enforcements.update_action_main(**kwargs)

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
