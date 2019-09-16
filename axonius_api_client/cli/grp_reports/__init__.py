# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context
from . import cmd_missing_adapters


@click.group()
@context.pass_context
def reports(ctx):
    """Work with device assets."""
    return ctx


reports.add_command(cmd_missing_adapters.cmd)
