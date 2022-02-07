# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ....tools import json_dump
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options

OPTIONS = [
    *AUTH,
    click.option(
        "--enable/--no-enable",
        "-e/-ne",
        "enabled",
        help="Enable / disable the central core feature",
        default=None,
        is_flag=True,
        show_envvar=True,
        show_default=True,
        required=True,
    ),
    click.option(
        "--delete-backups/--no-delete-backups",
        "-db/-ndb",
        "delete_backups",
        help="Delete backups once they are restored",
        default=None,
        is_flag=True,
        show_envvar=True,
        show_default=True,
        required=True,
    ),
]


@click.command(name="update", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, **kwargs):
    """Update the central core configuration."""
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.instances._update_central_core_config(**kwargs)
    click.secho(json_dump(data.config))
    ctx.exit(0)
