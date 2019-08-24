# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from . import context


@click.command("shell", context_settings=context.CONTEXT_SETTINGS)
@context.connect_options
@click.option(
    "--spawn/--no-spawn",
    default=True,
    help="Spawn an interactive shell",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@context.pass_context
def cmd(ctx, url, key, secret, spawn):
    """Start an interactive shell."""
    client = ctx.start_client(url=url, key=key, secret=secret, save_history=True)

    client._http.save_history = True

    devices = client.devices
    users = client.users
    adapters = client.adapters
    actions = client.actions
    enforcements = client.enforcements

    shellvars = {}
    shellvars.update(globals())
    shellvars.update(locals())

    if spawn:
        context.spawn_shell(shellvars)
    return ctx
