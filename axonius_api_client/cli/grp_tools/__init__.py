# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup
from . import cmd_shell, cmd_write_config


@click.group(cls=AliasedGroup)
def tools():
    """Group: CLI tools."""


tools.add_command(cmd_shell.cmd)
tools.add_command(cmd_write_config.cmd)
