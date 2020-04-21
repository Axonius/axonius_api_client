# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup


@click.group(cls=AliasedGroup)
def roles():
    """Group: Manage Roles."""
