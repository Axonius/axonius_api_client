# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import click

from ..context import AliasedGroup
from . import (grp_discover, grp_meta, grp_nodes,  # , grp_roles, grp_users
               grp_settings)


@click.group(cls=AliasedGroup)
def system():
    """Group: System control commands."""


system.add_command(grp_meta.meta)
system.add_command(grp_nodes.nodes)
# system.add_command(grp_roles.roles)  # XXX 3.3
system.add_command(grp_settings.settings_lifecycle)
system.add_command(grp_settings.settings_gui)
system.add_command(grp_settings.settings_core)
# system.add_command(grp_users.users)  # XXX 3.3
system.add_command(grp_discover.discover)
