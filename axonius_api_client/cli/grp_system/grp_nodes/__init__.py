# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup
from . import cmd_factory_reset, cmd_get


@click.group(cls=AliasedGroup)
def instances():
    """Group: Manage Instances."""


instances.add_command(cmd_get.cmd)
instances.add_command(cmd_factory_reset.cmd)
