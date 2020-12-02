# -*- coding: utf-8 -*-
"""Parsers for system objects."""
import math
from typing import List

from ..constants.system import Role, User
from ..tools import calc_gb, calc_perc_gb


def parse_sizes(raw: dict) -> dict:
    """Parse the disk usage metadata."""
    parsed = {}
    parsed["disk_free_mb"] = calc_gb(value=raw["disk_free"], is_kb=False)
    parsed["disk_used_mb"] = calc_gb(value=raw["disk_used"], is_kb=False)
    parsed["historical_sizes_devices"] = raw["entity_sizes"].get("Devices", {})
    parsed["historical_sizes_users"] = raw["entity_sizes"].get("Users", {})
    return parsed


def parse_instances(raw):
    """Parse instance data to add more maths.

    Args:
        raw: data returned from :meth:`axonius_api_client.api.system.instances.Instances._get`
    """
    for instance in raw["instances"]:
        calc_perc_gb(obj=instance, whole_key="data_disk_size", part_key="data_disk_free_space")
        calc_perc_gb(obj=instance, whole_key="memory_size", part_key="memory_free_space")
        calc_perc_gb(obj=instance, whole_key="swap_size", part_key="swap_free_space")
        calc_perc_gb(obj=instance, whole_key="os_disk_size", part_key="os_disk_free_space")
        instance["name"] = instance["node_name"]
        instance["id"] = instance["node_id"]
    return raw


def parse_cat_actions(raw: dict) -> dict:
    """Parse the permission labels into a layered dict.

    Args:
        raw: result from :meth:`axonius_api_client.api.system.system_roles.SystemRoles._get_labels`
    """

    def set_len(item, target):
        measure = int(math.ceil(len(item) / 10.0)) * 10
        if measure > lengths[target]:
            lengths[target] = measure

    cats = {}
    cat_actions = {}
    lengths = {Role.CATS: 0, Role.ACTS: 0, Role.CATS_DESC: 0, Role.ACTS_DESC: 0}

    # first pass, get all of the categories
    for label, desc in raw.items():
        pre, rest = label.split(".", 1)
        if pre != Role.PERMS_PRE:
            continue

        split = rest.split(".", 1)
        cat = split.pop(0)

        if not split:
            assert cat not in cats
            assert cat not in cat_actions
            cats[cat] = desc
            set_len(item=desc, target=Role.CATS_DESC)
            set_len(item=cat, target=Role.CATS)

            cat_actions[cat] = {}

    # second pass, get all of the actions
    for label, desc in raw.items():
        pre, rest = label.split(".", 1)
        if pre != Role.PERMS_PRE:
            continue

        split = rest.split(".", 1)
        cat = split.pop(0)

        if not split:
            continue

        # cat_desc = cats[cat]
        action = split.pop(0)
        assert not split
        assert action not in cat_actions[cat]
        set_len(item=desc, target=Role.ACTS_DESC)
        set_len(item=action, target=Role.ACTS)
        cat_actions[cat][action] = desc

    return {Role.CATS: cats, Role.ACTS: cat_actions, Role.LENS: lengths}


def parse_roles(roles: List[dict]) -> List[dict]:
    """Parse roles permissions into a flat structure.

    Args:
        roles: roles to parse
    """
    return [parse_role(role=x) for x in roles]


def parse_role(role: dict) -> dict:
    """Parse a roles permissions into a flat structure.

    Args:
        role: role to parse
    """
    role[Role.PERMS_FLAT] = parse_role_perms(perms=role[Role.PERMS])
    return role


def parse_role_perms(perms: dict) -> dict:
    """Parse a roles permissions into a flat structure.

    Args:
        role: role to parse
    """
    parsed = {}
    for cat, actions in perms.items():
        parsed[cat] = {}
        for action, value in actions.items():
            if isinstance(value, dict):
                for sub_cat, sub_value in value.items():
                    parsed[cat][f"{action}.{sub_cat}"] = sub_value
                continue

            parsed[cat][action] = value
    return parsed


'''
def parse_lifecycle(raw: dict) -> dict:
    """Parse the lifecycle metadata to add more user friendly data.

    Args:
        raw: return of lifecycle data from
            :meth:`axonius_api_client.api.system.dashboard.Dashboard._get`
    """
    parsed = {}

    finish_dt = raw["last_finished_time"]
    start_dt = raw["last_start_time"]

    if finish_dt:
        finish_dt = dt_parse(finish_dt)
    if start_dt:
        start_dt = dt_parse(start_dt)

    if (finish_dt and start_dt) and finish_dt >= start_dt:  # pragma: no cover
        took_seconds = (finish_dt - start_dt).seconds
        took_minutes = math.ceil(took_seconds / 60)
    else:
        took_minutes = -1

    next_seconds = raw["next_run_time"]
    next_minutes = math.ceil(next_seconds / 60)
    next_dt = dt_now() + timedelta(seconds=next_seconds)

    parsed["last_start_date"] = str(start_dt)
    parsed["last_finish_date"] = str(finish_dt)
    parsed["last_took_minutes"] = took_minutes

    parsed["next_start_date"] = str(next_dt)
    parsed["next_in_minutes"] = next_minutes

    parsed["is_running"] = not raw["status"] == "done"
    parsed["phases_done"] = [x["name"] for x in raw["sub_phases"] if x["status"] == 1]
    parsed["phases_pending"] = [x["name"] for x in raw["sub_phases"] if x["status"] != 1]
    parsed["phases"] = [parse_sub_phase(raw=x) for x in raw["sub_phases"]]
    return parsed


def parse_sub_phase(raw: dict) -> dict:
    """Parse a sub phase of lifecycle metadata to add more user friendly data.

    Args:
        raw: raw metadata of a lifecycle sub phase
    """
    parsed = {}
    parsed["is_done"] = raw["status"] == 1
    parsed["name"] = raw["name"]
    parsed["progress"] = {}
    for name, status in raw["additional_data"].items():  # pragma: no cover
        parsed["progress"][status] = parsed["progress"].get(status, [])
        parsed["progress"][status].append(name)
    return parsed
'''


def parse_user(user: dict, role_obj: dict) -> dict:
    """Parse a user to add role and other info.

    Args:
        user: user to parse
        role_obj: role object associated with user
    """
    first = user.get(User.FIRST_NAME, "")
    last = user.get(User.LAST_NAME, "")
    full = " ".join([x for x in [first, last] if x])
    role_name = role_obj[Role.NAME]

    user[User.ROLE_OBJ] = role_obj
    user[User.FULL_NAME] = full
    user[User.ROLE_NAME] = role_name
    return user
