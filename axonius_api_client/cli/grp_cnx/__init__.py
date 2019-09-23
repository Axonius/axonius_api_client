# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import click_ext
from . import cmd_add, cmd_check, cmd_delete, cmd_discover, cmd_get


@click.group(cls=click_ext.AliasedGroup)
def cnx():
    """Group: Work with adapter connections."""


cnx.add_command(cmd_add.cmd)
cnx.add_command(cmd_check.cmd)
cnx.add_command(cmd_delete.cmd)
cnx.add_command(cmd_discover.cmd)
cnx.add_command(cmd_get.cmd)
