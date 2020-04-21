# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup


@click.group(cls=AliasedGroup)
def settings_global():
    """Group: Global Settings."""


@click.group(cls=AliasedGroup)
def settings_lifecycle():
    """Group: Lifecycle Settings."""


@click.group(cls=AliasedGroup)
def settings_gui():
    """Group: GUI Settings."""
