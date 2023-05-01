# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import typing as t

import click

from ..context import AliasedGroup, load_cmds
from ..grp_tools import cmd_signup, cmd_use_token_reset_token, cmd_write_config


@click.group(cls=AliasedGroup)
def account():
    """Group: Account commands."""


load_cmds(path=__file__, package=__package__, group=account)

COMMANDS: t.List[t.Any] = [
    cmd_write_config.cmd,
    cmd_signup.cmd,
    cmd_use_token_reset_token.cmd,
]

for cmd in COMMANDS:
    account.add_command(cmd)
