# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup
from . import cmd_get


@click.group(cls=AliasedGroup)
def discover():
    """Group: Discover and Lifecycle management."""


discover.add_command(cmd_get.cmd)
