# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup
from . import (
    cmd_add,
    cmd_add_from_csv,
    cmd_delete,
    cmd_email_password_reset_link,
    cmd_get,
    cmd_get_by_name,
    cmd_get_password_reset_link,
    cmd_update,
)


@click.group(cls=AliasedGroup)
def users():
    """Group: Manage Users."""


users.add_command(cmd_get.cmd)
users.add_command(cmd_get_by_name.cmd)
users.add_command(cmd_update.cmd)
users.add_command(cmd_delete.cmd)
users.add_command(cmd_get_password_reset_link.cmd)
users.add_command(cmd_email_password_reset_link.cmd)
users.add_command(cmd_add.cmd)
users.add_command(cmd_add_from_csv.cmd)
