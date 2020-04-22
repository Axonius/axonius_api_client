# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup
from . import cmd_get, cmd_get_section, cmd_get_subsection


@click.group(cls=AliasedGroup)
def settings_core():
    """Group: Global Settings."""


@click.group(cls=AliasedGroup)
def settings_lifecycle():
    """Group: Lifecycle Settings."""


@click.group(cls=AliasedGroup)
def settings_gui():
    """Group: GUI Settings."""


CMDS = [cmd_get, cmd_get_section, cmd_get_subsection]

for cmd in CMDS:
    settings_core.add_command(cmd.cmd)
    settings_lifecycle.add_command(cmd.cmd)
    settings_gui.add_command(cmd.cmd)
