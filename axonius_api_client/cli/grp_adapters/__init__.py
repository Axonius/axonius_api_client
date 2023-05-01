# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import typing as t

import click

from ..context import AliasedGroup, load_cmds
from . import grp_cnx


@click.group(cls=AliasedGroup)
def adapters():
    """Group: Work with adapters and adapter connections."""


load_cmds(path=__file__, package=__package__, group=adapters)

GROUPS: t.List[t.Any] = [grp_cnx.cnx]
# Type hint doesn't recognize click.Group because of decorator?

for grp in GROUPS:
    adapters.add_command(grp)
