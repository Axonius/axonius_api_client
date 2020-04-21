# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...tools import json_dump
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, INPUT_FILE, NODE, add_options
from .grp_common import CONFIG_EXPORT, CONFIG_TYPE, config_export

OPTIONS = [*AUTH, CONFIG_EXPORT, CONFIG_TYPE, *NODE, INPUT_FILE]


@click.command(name="config-update-from-json", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, input_file, **kwargs):
    """Set adapter advanced settings from a JSON file."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    contents = ctx.obj.read_stream_json(stream=input_file, expect=dict)
    kwargs["kwargs_config"] = contents

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = client.adapters.config_update(**kwargs)
    ctx.obj.echo_ok(f"Updated adapter with config:\n{json_dump(contents)}")
    config_export(ctx=ctx, rows=rows, export_format=export_format)
