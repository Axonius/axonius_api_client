# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import click_ext, grp_cnx
from . import cmd_get


@click.group(cls=click_ext.AliasedGroup)
def adapters():
    """Group: Work with adapters and adapter connections."""


adapters.add_command(cmd_get.cmd)
adapters.add_command(grp_cnx.cnx)
