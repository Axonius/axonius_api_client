# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context, grp_cnx
from . import cmd_get


@click.group()
@context.pass_context
def adapters(ctx):
    """Work with adapter connections."""
    return ctx


adapters.add_command(cmd_get.cmd)
adapters.add_command(grp_cnx.cnx)
