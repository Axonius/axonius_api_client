# -*- coding: utf-8 -*-
"""API models for working with adapters and connections."""
from ...constants import ROLE_ACTIONS


def parse_roles_labels(raw):
    """Pass."""
    perms = {}
    descs = {}

    for perm, desc in raw.items():
        if not perm.startswith("permissions"):
            continue

        items = perm.split(".")
        items.pop(0)

        category = items.pop(0)
        if category not in perms:
            perms[category] = {}
            descs[category] = desc

        if not items:
            continue

        action = items.pop(0)

        if action in ROLE_ACTIONS:
            perms[category][action] = desc
        else:
            if action not in perms[category]:
                perms[category][action] = {}

            sub_action = items.pop(0)

            if sub_action in ROLE_ACTIONS:
                perms[category][action][sub_action] = desc

    return {"permissions": perms, "descriptions": descs}
