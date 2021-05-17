# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup
from . import cmd_add, cmd_delete, cmd_get, cmd_get_by_name, cmd_update_name, cmd_update_perms


@click.group(cls=AliasedGroup)
def roles():
    """Group: Manage Roles."""


roles.add_command(cmd_get.cmd)
roles.add_command(cmd_get_by_name.cmd)
roles.add_command(cmd_delete.cmd)
roles.add_command(cmd_add.cmd)
roles.add_command(cmd_update_name.cmd)
roles.add_command(cmd_update_perms.cmd)
