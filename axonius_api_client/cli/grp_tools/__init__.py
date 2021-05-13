# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup
from . import (
    cmd_convert_cert,
    cmd_shell,
    cmd_signup,
    cmd_sysinfo,
    cmd_system_status,
    cmd_use_token_reset_token,
    cmd_write_config,
)


@click.group(cls=AliasedGroup)
def tools():
    """Group: CLI tools."""


tools.add_command(cmd_shell.cmd)
tools.add_command(cmd_write_config.cmd)
tools.add_command(cmd_sysinfo.cmd)
tools.add_command(cmd_signup.cmd)
tools.add_command(cmd_convert_cert.cmd)
tools.add_command(cmd_use_token_reset_token.cmd)
tools.add_command(cmd_system_status.cmd)
