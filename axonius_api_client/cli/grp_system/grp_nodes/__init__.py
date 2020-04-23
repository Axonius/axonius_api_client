# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup
from . import cmd_get


@click.group(cls=AliasedGroup)
def nodes():
    """Group: Manage Nodes (Instances)."""


nodes.add_command(cmd_get.cmd)
