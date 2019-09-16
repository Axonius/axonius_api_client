# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from __future__ import absolute_import, division, print_function, unicode_literals

import click

from .. import context, grp_labels, grp_reports, grp_saved_query
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


@click.group()
@context.pass_context
def devices(ctx):
    """Work with device assets."""
    return ctx


@click.group()
@context.pass_context
def users(ctx):
    """Work with user assets."""
    return ctx


users.add_command(cmd_get.cmd)
users.add_command(cmd_fields.cmd)
users.add_command(cmd_count.cmd)
users.add_command(cmd_count_by_saved_query.cmd)
users.add_command(cmd_get_by_username.cmd)
users.add_command(cmd_get_by_mail.cmd)
users.add_command(cmd_get_by_saved_query.cmd)
users.add_command(grp_reports.reports)
users.add_command(grp_labels.labels)
users.add_command(grp_saved_query.saved_query)

devices.add_command(cmd_get.cmd)
devices.add_command(cmd_fields.cmd)
devices.add_command(cmd_count.cmd)
devices.add_command(cmd_count_by_saved_query.cmd)
devices.add_command(cmd_get_by_hostname.cmd)
devices.add_command(cmd_get_by_ip.cmd)
devices.add_command(cmd_get_by_mac.cmd)
devices.add_command(cmd_get_by_subnet.cmd)
devices.add_command(cmd_get_by_saved_query.cmd)
devices.add_command(grp_reports.reports)
devices.add_command(grp_labels.labels)
devices.add_command(grp_saved_query.saved_query)
