# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ...context import AliasedGroup, load_cmds


@click.group(cls=AliasedGroup)
def data_scopes():
    """Group: Manage Data Scopes."""


load_cmds(path=__file__, package=__package__, group=data_scopes)
