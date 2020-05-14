# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup
from . import (
    cmd_config_get,
    cmd_config_update,
    cmd_config_update_from_json,
    cmd_file_upload,
    cmd_get,
    grp_cnx,
)


@click.group(cls=AliasedGroup)
def adapters():
    """Group: Work with adapters and adapter connections."""


adapters.add_command(cmd_get.cmd)
adapters.add_command(cmd_config_get.cmd)
adapters.add_command(cmd_config_update.cmd)
adapters.add_command(cmd_config_update_from_json.cmd)
adapters.add_command(cmd_file_upload.cmd)
adapters.add_command(grp_cnx.cnx)
