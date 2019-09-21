# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import click_ext
from . import cmd_add, cmd_get, cmd_remove


@click.group(cls=click_ext.AliasedGroup)
def labels():  # noqa:D402
    """Group: Work with labels (tags) for assets."""


labels.add_command(cmd_get.cmd)
labels.add_command(cmd_add.cmd)
labels.add_command(cmd_remove.cmd)
