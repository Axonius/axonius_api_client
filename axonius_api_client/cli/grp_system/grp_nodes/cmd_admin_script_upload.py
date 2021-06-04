# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

PATH = click.option(
    "--path",
    "-p",
    "path",
    help="URL or path of admin script file to upload & execute",
    required=True,
    show_envvar=True,
    show_default=True,
)

OPTIONS = [
    *AUTH,
    PATH,
]


@click.command(name="admin-script-upload", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, path, **kwargs):
    """Upload an admin script from a URL or file and execute it."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.instances.admin_script_upload_path(path=path)

    click.secho(json_dump(data))
    ctx.exit(0)
