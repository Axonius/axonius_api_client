# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup
from . import cmd_add, cmd_get, cmd_remove


@click.group(cls=AliasedGroup)
def labels():  # noqa:D402
    """Group: Work with labels (tags) for assets."""


labels.add_command(cmd_get.cmd)
labels.add_command(cmd_add.cmd)
labels.add_command(cmd_remove.cmd)
