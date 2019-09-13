# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context
from . import cmd_fields, cmd_get, cmd_missing_adapters


@click.group()
@context.pass_context
def devices(ctx):
    """Work with device assets."""
    return ctx


@click.group()
@context.pass_context
def users(ctx):
    """Work with user assets."""
    return ctx


users.add_command(cmd_get.cmd)
users.add_command(cmd_fields.cmd)
users.add_command(cmd_missing_adapters.cmd)

devices.add_command(cmd_get.cmd)
devices.add_command(cmd_fields.cmd)
devices.add_command(cmd_missing_adapters.cmd)


__all__ = ("cmd_fields", "cmd_get", "cmd_missing_adapters", "devices", "users")
