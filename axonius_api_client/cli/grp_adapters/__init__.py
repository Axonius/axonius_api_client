# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup
from ..grp_cnx import cnx
from . import (
    cmd_config_get,
    cmd_config_update,
    cmd_config_update_file,
    cmd_file_upload,
    cmd_get,
)


@click.group(cls=AliasedGroup)
def adapters():
    """Group: Work with adapters and adapter connections."""


adapters.add_command(cmd_get.cmd)
adapters.add_command(cmd_config_get.cmd)
adapters.add_command(cmd_config_update.cmd)
adapters.add_command(cmd_config_update_file.cmd)
adapters.add_command(cmd_file_upload.cmd)
adapters.add_command(cnx)
