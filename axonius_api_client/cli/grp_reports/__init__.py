# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import click_ext
from . import cmd_missing_adapters


@click.group(cls=click_ext.AliasedGroup)
def reports():
    """Group: Work with reports for assets."""


reports.add_command(cmd_missing_adapters.cmd)
