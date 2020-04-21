# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup
from . import cmd_add, cmd_delete, cmd_get, cmd_update, cmd_update_role


@click.group(cls=AliasedGroup)
def users():
    """Group: Manage Users."""


users.add_command(cmd_get.cmd)
users.add_command(cmd_update_role.cmd)
users.add_command(cmd_update.cmd)
users.add_command(cmd_add.cmd)
users.add_command(cmd_delete.cmd)
