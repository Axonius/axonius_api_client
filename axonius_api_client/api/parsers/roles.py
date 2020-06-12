# -*- coding: utf-8 -*-
"""API models for working with adapters and connections."""
# from ...constants import ROLE_ACTIONS
# from ...tools import strip_left


def parse_permissions(raw, default_perm=False):
    """Pass."""
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
