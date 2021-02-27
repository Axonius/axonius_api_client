# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup
from . import cmd_configure, cmd_configure_analytics, cmd_configure_remote_access, cmd_get


@click.group(cls=AliasedGroup)
def remote_support():
    """Group: Manage Remote Support configuration."""


remote_support.add_command(cmd_get.cmd)
remote_support.add_command(cmd_configure.cmd)
remote_support.add_command(cmd_configure_analytics.cmd)
remote_support.add_command(cmd_configure_remote_access.cmd)
