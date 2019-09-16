# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context
from . import cmd_add, cmd_get, cmd_remove


@click.group()
@context.pass_context
def labels(ctx):
    """Work with device assets."""
    return ctx


labels.add_command(cmd_get.cmd)
labels.add_command(cmd_add.cmd)
labels.add_command(cmd_remove.cmd)
