# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup, load_cmds
from . import grp_cnx


@click.group(cls=AliasedGroup)
def adapters():
    """Group: Work with adapters and adapter connections."""


load_cmds(path=__file__, package=__package__, group=adapters)
adapters.add_command(grp_cnx.cnx)
