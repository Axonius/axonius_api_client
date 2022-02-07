# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import json_dump
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, NODE, SPLIT_CONFIG_REQ, add_options
from .grp_common import CONFIG_EXPORT, CONFIG_EXPORT_FORMATS, CONFIG_TYPE

OPTIONS = [*AUTH, CONFIG_EXPORT, CONFIG_TYPE, *NODE, SPLIT_CONFIG_REQ]


@click.command(name="config-update", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, config, **kwargs):
    """Set adapter advanced settings."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    config = dict(config)
    kwargs["kwargs_config"] = config

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.adapters.config_update(**kwargs)
    ctx.obj.echo_ok(f"Updated adapter with config:\n{json_dump(config)}")
    click.secho(CONFIG_EXPORT_FORMATS[export_format](data=data))
    ctx.exit(0)
