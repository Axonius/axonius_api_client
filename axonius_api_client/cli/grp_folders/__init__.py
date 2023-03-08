# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup
from .grp_enforcements import enforcements
from .grp_queries import queries


@click.group(cls=AliasedGroup)
def folders():
    """Group: Work with folders."""


folders.add_command(queries)
folders.add_command(enforcements)
