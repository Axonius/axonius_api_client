# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup, load_cmds
from ..grp_tools import cmd_signup, cmd_use_token_reset_token, cmd_write_config


@click.group(cls=AliasedGroup)
def account():
    """Group: Account commands."""


load_cmds(path=__file__, package=__package__, group=account)
account.add_command(cmd_write_config.cmd)
account.add_command(cmd_signup.cmd)
account.add_command(cmd_use_token_reset_token.cmd)
