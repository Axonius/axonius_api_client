# -*- coding: utf-8 -*-
"""Parsers for dashboards and discovery cycles."""
import math

from ..tools import dt_now, dt_parse, timedelta


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
        parsed["progress"][status] = parsed["progress"].get(status)
        parsed["progress"][status].append(name)
    return parsed
