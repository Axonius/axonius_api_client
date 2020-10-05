# -*- coding: utf-8 -*-
"""Parsers for system roles."""


def parse_permissions(raw, default_perm=False):  # pragma: no cover
    """Parse the permissions for roles.

    Args:
        raw: role labels returned from
            :meth:`axonius_api_client.api.system.system_roles.SystemRoles._get_labels`
        default_perm: default permission to assign for roles
    """
    actions = {}
    categories = {}

    for permission, description in raw.items():
        if not permission.startswith("permissions."):
            continue

        permission_split = permission.split(".")[1:]
        category = permission_split[0]

        if len(permission_split) == 1:
            categories[category] = description

    for permission, description in raw.items():
        if not permission.startswith("permissions."):
            continue

        permission_split = permission.split(".")[1:]
        category = permission_split[0]
        category_description = categories[category]

        if len(permission_split) > 1:
            action = ".".join(permission_split)
            actions[action] = f"{category_description}: {description}"

    return actions
