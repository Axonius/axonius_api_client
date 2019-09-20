# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from . import context


@click.command(name="shell", context_settings=context.CONTEXT_SETTINGS)
@context.OPT_URL
@context.OPT_KEY
@context.OPT_SECRET
@context.pass_context
def cmd(ctx, url, key, secret):  # noqa: D301
    """Start an interactive python shell.

    The shell will authenticate to Axonius, setup autocompletion, enable history,
    and create the following objects:

    \b
        - client: Instance of axonius_api_client.connect.Connect
        - devices: Instance of axonius_api_client.api.Devices
        - users: Instance of axonius_api_client.api.Users
        - adapters: Instance of axonius_api_client.api.Adapters
        - enforcements: Instance of axonius_api_client.api.Enforcements
        - jdump: Helper function to pretty print python objects

    """
    client = ctx.start_client(url=url, key=key, secret=secret, save_history=True)

    client._http.save_history = True

    devices = client.devices
    users = client.users
    adapters = client.adapters
    enforcements = client.enforcements

    shellvars = {}
    shellvars.update(globals())
    shellvars.update(locals())

    context.spawn_shell(shellvars)
