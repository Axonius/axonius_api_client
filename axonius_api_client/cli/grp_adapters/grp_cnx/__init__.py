# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ... import context
from . import (
    cmd_add,
    cmd_add_from_json,
    cmd_add_multiple_from_json,
    cmd_delete_by_id,
    cmd_get,
    cmd_get_by_id,
    cmd_set_active,
    cmd_set_label,
    cmd_test,
    cmd_test_by_id,
)


@click.group(cls=context.AliasedGroup)
def cnx():
    """Group: Work with adapter connections."""


cnx.add_command(cmd_add.cmd)
cnx.add_command(cmd_add_from_json.cmd)
cnx.add_command(cmd_add_multiple_from_json.cmd)
cnx.add_command(cmd_get.cmd)
cnx.add_command(cmd_get_by_id.cmd)
cnx.add_command(cmd_delete_by_id.cmd)
cnx.add_command(cmd_test.cmd)
cnx.add_command(cmd_test_by_id.cmd)
cnx.add_command(cmd_set_label.cmd)
cnx.add_command(cmd_set_active.cmd)
