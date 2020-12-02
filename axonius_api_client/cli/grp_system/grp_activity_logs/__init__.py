# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup
from . import cmd_get


@click.group(cls=AliasedGroup)
def activity_logs():
    """Group: Work with Activity Logs."""


activity_logs.add_command(cmd_get.cmd)
