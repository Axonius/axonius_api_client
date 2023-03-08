# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup, load_cmds


@click.group(cls=AliasedGroup)
def folders():
    """Group: Work with folders."""


@click.group(cls=AliasedGroup)
def enforcements():
    """Group: Work with folders for Enforcements."""


@click.group(cls=AliasedGroup)
def queries():
    """Group: Work with folders for Queries."""


GROUPS = [enforcements, queries]

for group in GROUPS:
    folders.add_command(group)
    load_cmds(path=__file__, package=__package__, group=group)
