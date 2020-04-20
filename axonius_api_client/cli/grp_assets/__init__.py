# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from .. import grp_saved_query
from ..context import AliasedGroup
from . import (
    cmd_count,
    cmd_count_by_saved_query,
    cmd_fields,
    cmd_get,
    cmd_get_by_hostname,
    cmd_get_by_ip,
    cmd_get_by_mac,
    cmd_get_by_mail,
    cmd_get_by_saved_query,
    cmd_get_by_subnet,
    cmd_get_by_username,
)


@click.group(cls=AliasedGroup)
def devices():
    """Group: Work with device assets."""


@click.group(cls=AliasedGroup)
def users():
    """Group: Work with user assets."""


CMDS = [
    # grp_labels.labels,  # XXX ADD AS OPTS TO GET*
    grp_saved_query.saved_query,
    cmd_count.cmd,
    cmd_count_by_saved_query.cmd,
    cmd_fields.cmd,
    cmd_get.cmd,
    cmd_get_by_saved_query.cmd,
]

for cmd in CMDS:
    users.add_command(cmd)
    devices.add_command(cmd)

users.add_command(cmd_get_by_mail.cmd)
users.add_command(cmd_get_by_username.cmd)

devices.add_command(cmd_get_by_hostname.cmd)
devices.add_command(cmd_get_by_ip.cmd)
devices.add_command(cmd_get_by_mac.cmd)
devices.add_command(cmd_get_by_subnet.cmd)
