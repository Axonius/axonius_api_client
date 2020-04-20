# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ... import context
from . import cmd_add, cmd_get, cmd_get_by_id


@click.group(cls=context.AliasedGroup)
def cnx():
    """Group: Work with adapter connections."""


cnx.add_command(cmd_add.cmd)
cnx.add_command(cmd_get.cmd)
cnx.add_command(cmd_get_by_id.cmd)
