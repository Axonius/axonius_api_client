# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup
from . import (
    grp_central_core,
    grp_discover,
    grp_meta,
    grp_nodes,
    grp_roles,
    grp_settings,
    grp_users,
)


@click.group(cls=AliasedGroup)
def system():
    """Group: System control commands."""


system.add_command(grp_meta.meta)
system.add_command(grp_nodes.nodes)
system.add_command(grp_central_core.central_core)
system.add_command(grp_roles.roles)
system.add_command(grp_settings.settings_lifecycle)
system.add_command(grp_settings.settings_gui)
system.add_command(grp_settings.settings_core)
system.add_command(grp_users.users)
system.add_command(grp_discover.discover)
