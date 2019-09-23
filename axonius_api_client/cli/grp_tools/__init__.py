# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import click_ext
from . import cmd_shell, cmd_write_config


@click.group(cls=click_ext.AliasedGroup)
def tools():
    """Group: CLI tools."""


tools.add_command(cmd_shell.cmd)
tools.add_command(cmd_write_config.cmd)
