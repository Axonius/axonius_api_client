# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup
from . import cmd_get, cmd_is_data_stable, cmd_is_running, cmd_start, cmd_stop, cmd_wait_data_stable


@click.group(cls=AliasedGroup)
def discover():
    """Group: Discover and Lifecycle management."""


discover.add_command(cmd_get.cmd)
discover.add_command(cmd_start.cmd)
discover.add_command(cmd_stop.cmd)
discover.add_command(cmd_is_running.cmd)
discover.add_command(cmd_is_data_stable.cmd)
discover.add_command(cmd_wait_data_stable.cmd)
