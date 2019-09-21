# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import click_ext
from . import cmd_add, cmd_delete, cmd_get, cmd_get_by_name


@click.group(cls=click_ext.AliasedGroup)
def saved_query():
    """Group: Work with saved queries."""


saved_query.add_command(cmd_add.cmd)
saved_query.add_command(cmd_delete.cmd)
saved_query.add_command(cmd_get.cmd)
saved_query.add_command(cmd_get_by_name.cmd)
