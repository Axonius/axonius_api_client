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
@context.common_options
@click.option(
    "--spawn/--no-spawn",
    default=True,
    help="Spawn an interactive shell",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@context.pass_context
@click.pass_context
def shell(clickctx, ctx, spawn=True, **kwargs):
    """Start an interactive shell."""
    for k, v in kwargs.items():
        setattr(ctx, k, v)

    client = ctx.start_client()

    shellvars = globals()
    shellvars.update(locals())

    readline.set_completer(rlcompleter.Completer(shellvars).complete)
    readline.parse_and_bind("tab: complete")

    if spawn:
        code.interact(local=shellvars)
    return ctx
