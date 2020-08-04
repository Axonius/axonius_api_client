# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
import math

from ...tools import dt_now, dt_parse, timedelta
from ..mixins import ChildMixins


class Discover(ChildMixins):
    """Child API model for working with discovery cycles."""

    def get(self) -> dict:
        """Get lifecycle metadata.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        return parse_lifecycle(raw=self._get())

    @property
    def is_running(self) -> bool:
        """Check if discovery cycle is running.

        Returns:
            :obj:`bool`: if discovery cycle is running
        """
        return self.get()["is_running"]

    def start(self) -> dict:
        """Start a discovery cycle if one is not running.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        if not self.is_running:
            self._start()
        return self.get()

    def stop(self) -> dict:
        """Stop a discovery cycle if one is running.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        if self.is_running:
            self._stop()
        return self.get()

    def _get(self) -> dict:
        """Direct API method to get discovery cycle metadata.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        path = self.router.discover_lifecycle
        return self.request(method="get", path=path)

    def _start(self) -> str:
        """Direct API method to start a discovery cycle."""
        path = self.router.discover_start
        return self.request(method="post", path=path)

    def _stop(self) -> str:
        """Direct API method to stop a discovery cycle.

        Returns:
            :obj:`dict`: discovery cycle metadata
        """
        path = self.router.discover_stop
        return self.request(method="post", path=path)


def parse_lifecycle(raw: dict) -> dict:
    """Pass."""
    parsed = {}

    finish_dt = raw["last_finished_time"]
    start_dt = raw["last_start_time"]

    if finish_dt:
        finish_dt = dt_parse(finish_dt)
    if start_dt:
        start_dt = dt_parse(start_dt)

    if (finish_dt and start_dt) and finish_dt >= start_dt:
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
    """Pass."""
    parsed = {}
    parsed["is_done"] = raw["status"] == 1
    parsed["name"] = raw["name"]
    parsed["progress"] = {}
    for name, status in raw["additional_data"].items():
        if status not in parsed["progress"]:
            parsed["progress"][status] = []
        parsed["progress"][status].append(name)
    return parsed
