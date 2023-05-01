# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click
import typing as t

from ..context import AliasedGroup, load_cmds
from . import grp_tasks


@click.group(cls=AliasedGroup)
def enforcements():
    """Group: Work with the Enforcement Center."""


load_cmds(path=__file__, package=__package__, group=enforcements)
GROUPS: t.List[t.Any] = [grp_tasks.tasks]
for grp in GROUPS:
    enforcements.add_command(grp)
