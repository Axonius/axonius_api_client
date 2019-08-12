# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import click

from . import context, cmd_object_fields, cmd_shell
from .. import tools

AX_DOTENV = os.environ.get("AX_DOTENV", "")
CWD_PATH = tools.resolve_path(os.getcwd())


# FUTURE: prompt does not use CR when re-prompting on empty var with hide_input=False
# FUTURE: add doc links
@click.group()
@context.pass_context
def cli(ctx, **kwargs):
    """Axonius API Client command line tool."""
    return ctx


@cli.group()
@context.pass_context
def devices(ctx):
    """Work with device objects."""
    return ctx


@cli.group()
@context.pass_context
def users(ctx):
    """Work with user objects."""
    return ctx


@cli.group()
@context.pass_context
def adapters(ctx):
    """Work with adapter objects."""
    return ctx


cli.add_command(cmd_shell.shell)
devices.add_command(cmd_object_fields.cmd)
users.add_command(cmd_object_fields.cmd)


def main(*args, **kwargs):
    """Pass."""
    context.load_dotenv()
    # kwargs.setdefault("auto_envvar_prefix", "ax")
    return cli(*args, **kwargs)


if __name__ == "__main__":
    main()

# report of all adapters missing from all devices
# report of all adapters missing from all users

# adapters field missing any clients configured for any adapters?
# fetch time field? older than N days?

# report of broken adapter clients
