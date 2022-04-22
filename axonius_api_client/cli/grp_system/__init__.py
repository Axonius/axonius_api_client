# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup
from . import (
    grp_activity_logs,
    grp_central_core,
    grp_data_scopes,
    grp_discover,
    grp_meta,
    grp_nodes,
    grp_remote_support,
    grp_roles,
    grp_settings,
    grp_users,
)


@click.group(cls=AliasedGroup)
def system():
    """Group: System control commands."""


system.add_command(grp_meta.meta)
system.add_command(grp_nodes.instances)
system.add_command(grp_central_core.central_core)
system.add_command(grp_roles.roles)
system.add_command(grp_settings.settings_lifecycle)
system.add_command(grp_settings.settings_gui)
system.add_command(grp_settings.settings_global)
system.add_command(grp_users.users)
system.add_command(grp_discover.discover)
system.add_command(grp_remote_support.remote_support)
system.add_command(grp_activity_logs.activity_logs)
system.add_command(grp_data_scopes.data_scopes)
