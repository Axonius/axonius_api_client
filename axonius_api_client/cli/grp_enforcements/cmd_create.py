# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ..context import CONTEXT_SETTINGS, click
from ..grp_folders.grp_options import OPTS_OBJECT_CREATE
from ..options import AUTH, add_options
from .grp_common import EXPORT_FORMATS, OPT_EXPORT_FORMAT, OPTS_CREATE

OPTIONS = [*AUTH, OPT_EXPORT_FORMAT, *OPTS_CREATE, *OPTS_OBJECT_CREATE]


@click.command(name="create", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, main_action_config, **kwargs):
    """Create an Enforcement Set."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    kwargs["main_action_config"] = ctx.obj.read_stream_json(stream=main_action_config, expect=dict)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.enforcements.create(**kwargs)

    click.secho(EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
