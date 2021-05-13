# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup
from . import (
    cmd_configure_destroy,
    cmd_get,
    cmd_get_section,
    cmd_get_subsection,
    cmd_update_section,
    cmd_update_section_from_json,
    cmd_update_subsection,
    cmd_update_subsection_from_json,
)


@click.group(cls=AliasedGroup)
def settings_global():
    """Group: Global Settings."""


@click.group(cls=AliasedGroup)
def settings_lifecycle():
    """Group: Lifecycle Settings."""


@click.group(cls=AliasedGroup)
def settings_gui():
    """Group: GUI Settings."""


CMDS = [
    cmd_get,
    cmd_get_section,
    cmd_get_subsection,
    cmd_update_section,
    cmd_update_subsection,
    cmd_update_section_from_json,
    cmd_update_subsection_from_json,
]

for cmd in CMDS:
    settings_global.add_command(cmd.cmd)
    settings_lifecycle.add_command(cmd.cmd)
    settings_gui.add_command(cmd.cmd)

settings_global.add_command(cmd_configure_destroy.cmd)
