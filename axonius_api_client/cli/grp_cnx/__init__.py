# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context
from . import cmd_get


@click.group()
@context.pass_context
def cnx(ctx):
    """Work with adapter connections."""
    return ctx


cnx.add_command(cmd_get.cmd)

__all__ = ("cmd_get", "cnx")
