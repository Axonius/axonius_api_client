# -*- coding: utf-8 -*-
"""API for working with dashboards and discovery lifecycle."""
import dataclasses
import datetime
from typing import Dict, List, Optional

from ...data import PropsData
from ...tools import coerce_int, dt_now, dt_parse, trim_float
from ..mixins import ModelMixins
from ..routers import API_VERSION, Router

PROPERTIES_PHASE: List[str] = ["name", "human_name", "is_done", "progress"]
PROPERTIES: List[str] = [
    "is_running",
    "is_correlation_finished",
    "status",
    "current_run_duration_in_minutes",
    "last_run_finish_date",
    "last_run_start_date",
    "last_run_duration_in_minutes",
    "last_run_minutes_ago",
    "next_run_start_date",
    "next_run_starts_in_minutes",
]


@dataclasses.dataclass
class DiscoverPhase(PropsData):
    """Pass."""

    raw: dict

    def to_str_properties(self) -> List[str]:
        """Pass."""
        return [f"Name: {self.human_name}", f"Is Done: {self.is_done}"]

    def to_str_progress(self) -> List[str]:
        """Pass."""
        return [f"{k}: {', '.join(v)}" for k, v in self.progress.items()]

    @property
    def _properties(self) -> List[str]:
        return PROPERTIES_PHASE

    @property
    def name(self) -> str:
        """Pass."""
        return self.raw["name"]

    @property
    def human_name(self) -> str:
        """Pass."""
        return self.name_map.get(self.name, self._human_key(self.name))

    @property
    def is_done(self) -> bool:
        """Pass."""
        return self.raw["status"] == 1

    @property
    def progress(self) -> Dict[str, List[str]]:
        """Pass."""
        items = self.raw["additional_data"].items()
        return {status: [k for k, v in items if v == status] for _, status in items}

    @property
    def name_map(self) -> dict:
        """Pass."""
        return {
            "Fetch_Devices": "Fetch Stage 1",
            "Fetch_Scanners": "Fetch Stage 2",
            "Clean_Devices": "Clean Assets",
            "Pre_Correlation": "Correlation Pre",
            "Run_Correlations": "Correlation Run",
            "Post_Correlation": "Correlation Post",
            "Run_Queries": "Calculate Queries",
            "Save_Historical": "Save History Snapshot",
        }


@dataclasses.dataclass
class DiscoverData(PropsData):
    """Pass."""

    raw: dict
    adapters: List[dict]

    @property
    def _properties(self) -> List[str]:
        return PROPERTIES

    def to_str_progress(self) -> List[str]:
        """Pass."""
        return [x["str"] for x in self.progress]

    def to_str_phases(self) -> List[str]:
        """Pass."""
        return [f"{x.human_name}: {x.status}" for x in self.phases]

    def to_dict(self, dt_obj: bool = False) -> dict:
        """Pass."""
        ret = super().to_dict(dt_obj=dt_obj)
        ret["phases"] = [x.to_dict() for x in self.phases]
        ret["progress"] = self.progress
        return ret

    @property
    def last_run_finish_date(self) -> Optional[datetime.datetime]:
        """Pass."""
        dt = self.raw["last_finished_time"]
        return dt_parse(obj=dt) if dt else None

    @property
    def last_run_start_date(self) -> Optional[datetime.datetime]:
        """Pass."""
        dt = self.raw["last_start_time"]
        return dt_parse(obj=dt) if dt else None

    @property
    def current_run_duration_in_minutes(self) -> Optional[float]:
        """Pass."""
        dt = self.last_run_start_date
        return trim_float(value=(dt_now() - dt).total_seconds() / 60) if self.is_running else None

    @property
    def last_run_duration_in_minutes(self) -> Optional[float]:
        """Pass."""
        start = self.last_run_start_date
        finish = self.last_run_finish_date
        check = (start and finish) and finish >= start

        return trim_float(value=(finish - start).total_seconds() / 60) if check else None

    @property
    def last_run_minutes_ago(self) -> Optional[float]:
        """Pass."""
        finish = self.last_run_finish_date
        return trim_float(value=(dt_now() - finish).total_seconds() / 60) if finish else None

    @property
    def next_run_starts_in_minutes(self) -> float:
        """Pass."""
        return trim_float(value=self.raw["next_run_time"] / 60)

    @property
    def next_run_start_date(self) -> datetime.datetime:
        """Pass."""
        return dt_now() + datetime.timedelta(seconds=self.raw["next_run_time"])

    @property
    def correlation_stage(self) -> str:
        """Pass."""
        return "Post_Correlation"

    @property
    def is_correlation_finished(self) -> bool:
        """Pass."""
        stage = self.correlation_stage
        not_running = not self.is_running
        return any([not_running, *[x.name == stage and x.is_done for x in self.phases]])

    @property
    def is_running(self) -> bool:
        """Pass."""
        return self.status != "done"

    @property
    def status(self) -> str:
        """Pass."""
        return self.raw["status"]

    @property
    def progress(self) -> List[dict]:
        """Pass."""
        plugin_map = {x["name_plugin"]: x for x in self.adapters}

        ret = []

        for phase in self.phases:
            for status, plugin_names in phase.progress.items():
                for plugin_name in plugin_names:  # pragma: no cover
                    adapter = plugin_map.get(plugin_name, {})
                    value = {
                        "node": adapter.get("node_name", "unknown"),
                        "adapter": adapter.get("name", plugin_name),
                        "status": status,
                    }
                    value["str"] = ", ".join(f"{self._human_key(k)}: {v}" for k, v in value.items())
                    ret.append(value)
        return ret

    @property
    def phases(self) -> List[DiscoverPhase]:
        """Pass."""
        self._has_running = False

        def get_status(phase):  # pragma: no cover
            if not self.is_running:
                return "n/a"

            if phase.is_done:
                return "done"

            if self._has_running:
                return "pending"

            self._has_running = True
            return "running"

        def get_phase(raw):
            phase = DiscoverPhase(raw=raw)
            phase.status = get_status(phase)
            return phase

        return [get_phase(x) for x in self.raw["sub_phases"]]

    def next_run_within_minutes(self, value: int) -> bool:
        """Pass."""
        return coerce_int(obj=value, min_value=0) >= int(self.next_run_starts_in_minutes)


class Dashboard(ModelMixins):
    """API for working with dashboards and discovery lifecycle.

    Examples:
        * Get discover lifecycle metadata: :meth:`get`
        * See if a lifecycle is currently running: :meth:`is_running`
        * Start a discover lifecycle: :meth:`start`
        * Stop a discover lifecycle: :meth:`stop`

    """

    def get(self) -> DiscoverData:
        """Get lifecycle metadata.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.get()
            >>> data.next_run_starts_in_minutes
            551
            >>> data.is_running
            False
        """
        return DiscoverData(raw=self._get(), adapters=self.adapters.get())

    @property
    def is_running(self) -> bool:
        """Check if discovery cycle is running.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.is_running
            False
        """
        return self.get().is_running

    def start(self) -> DiscoverData:
        """Start a discovery cycle if one is not running.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.start()
            >>> data.is_running
            True
            >>> j(data['phases_pending'])
            [
              "Fetch_Devices",
              "Fetch_Scanners",
              "Clean_Devices",
              "Pre_Correlation",
              "Run_Correlations",
              "Post_Correlation",
              "Run_Queries",
              "Save_Historical"
            ]
            >>> j(data['phases_done'])
            []

        """
        if not self.is_running:
            self._start()
        return self.get()

    def stop(self) -> DiscoverData:
        """Stop a discovery cycle if one is running.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.start()
            >>> data.is_running
            True
        """
        if self.is_running:
            self._stop()
        return self.get()

    def _get(self) -> dict:
        """Direct API method to get discovery cycle metadata."""
        path = self.router.lifecycle
        return self.request(method="get", path=path)

    def _start(self) -> str:
        """Direct API method to start a discovery cycle."""
        path = self.router.discover_start
        return self.request(method="post", path=path)

    def _stop(self) -> str:
        """Direct API method to stop a discovery cycle."""
        path = self.router.discover_stop
        return self.request(method="post", path=path)

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.dashboard

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        from ..adapters.adapters import Adapters

        self.adapters: Adapters = Adapters(auth=self.auth)
        """Work with adapters"""
