# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup


@click.group(cls=AliasedGroup)
def users():
    """Group: Manage Users."""
