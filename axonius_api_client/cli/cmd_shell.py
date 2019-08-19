# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import code
import readline
import rlcompleter
import json

import click

from . import context


def jdump(obj):
    """JSON dump utility."""
    print(json.dumps(obj, indent=2))


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
def shell(ctx, url, key, secret, spawn):
    """Start an interactive shell."""
    client = ctx.start_client(
        url=url, key=key, secret=secret, log_attrs_request=True, save_history=True
    )

    if spawn:
        shellvars = globals()
        shellvars.update(locals())

        readline.set_completer(rlcompleter.Completer(shellvars).complete)
        readline.parse_and_bind("tab: complete")

        code.interact(local=shellvars)
    return ctx
