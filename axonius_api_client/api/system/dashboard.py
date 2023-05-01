# -*- coding: utf-8 -*-
"""API for working with dashboards and discovery lifecycle."""
import dataclasses
import datetime
import time
import typing as t

from ...data import PropsData
from ...tools import coerce_int, dt_now, dt_parse, trim_float
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ModelMixins

PROPERTIES_PHASE: t.List[str] = ["name", "human_name", "is_done", "progress"]
PROPERTIES: t.List[str] = [
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

    def to_str_properties(self) -> t.List[str]:
        """Pass."""
        return [f"Name: {self.human_name}", f"Is Done: {self.is_done}"]

    def to_str_progress(self) -> t.List[str]:
        """Pass."""
        return [f"{k}: {', '.join(v)}" for k, v in self.progress.items()]

    @property
    def _properties(self) -> t.List[str]:
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
    def progress(self) -> t.Dict[str, t.List[str]]:
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
    adapters: t.List[dict] = dataclasses.field(default_factory=list, repr=False)

    @property
    def _properties(self) -> t.List[str]:
        return PROPERTIES

    def to_str_progress(self) -> t.List[str]:
        """Pass."""
        return [x["str"] for x in self.progress]

    def to_str_phases(self) -> t.List[str]:
        """Pass."""
        return [f"{x.human_name}: {x.status}" for x in self.phases]

    @property
    def phases_dict(self) -> dict:
        """Pass."""
        return {x.name: x for x in self.phases}

    def to_dict(self, dt_obj: bool = False) -> dict:
        """Pass."""
        ret = super().to_dict(dt_obj=dt_obj)
        ret["phases"] = [x.to_dict() for x in self.phases]
        ret["progress"] = self.progress
        return ret

    @property
    def last_run_finish_date(self) -> t.Optional[datetime.datetime]:
        """Pass."""
        dt = self.raw["last_finished_time"]
        return dt_parse(obj=dt) if dt else None

    @property
    def last_run_start_date(self) -> t.Optional[datetime.datetime]:
        """Pass."""
        dt = self.raw["last_start_time"]
        return dt_parse(obj=dt) if dt else None

    @property
    def current_run_duration_in_minutes(self) -> t.Optional[float]:
        """Pass."""
        dt = self.last_run_start_date
        return trim_float(value=(dt_now() - dt).total_seconds() / 60) if self.is_running else None

    @property
    def last_run_duration_in_minutes(self) -> t.Optional[float]:
        """Pass."""
        start = self.last_run_start_date
        finish = self.last_run_finish_date
        check = (start and finish) and finish >= start

        return trim_float(value=(finish - start).total_seconds() / 60) if check else None

    @property
    def last_run_minutes_ago(self) -> t.Optional[float]:
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
    def correlation_phase(self) -> t.Optional[DiscoverPhase]:
        """Pass."""
        return self.phases_dict.get(self.correlation_stage)

    @property
    def is_correlation_finished(self) -> bool:
        """Pass."""
        if not self.is_running:
            return True
        elif isinstance(self.correlation_phase, DiscoverPhase) and self.correlation_phase.is_done:
            return True
        return False

    @property
    def running_status_map(self) -> dict:
        """Pass."""
        return {
            "done": False,
            "stopping": False,
            "starting": True,
            "running": True,
        }

    @property
    def is_running(self) -> bool:
        """Pass."""
        return self.running_status_map.get(self.status, False)

    @property
    def status(self) -> str:
        """Pass."""
        return self.raw["status"]

    @property
    def progress(self) -> t.List[dict]:
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
    def phases(self) -> t.List[DiscoverPhase]:
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

    def next_run_within_minutes(self, value: t.Union[int, str]) -> bool:
        """Pass."""
        return coerce_int(obj=value, min_value=0) >= int(self.next_run_starts_in_minutes)

    def get_stability(
        self, for_next_minutes: t.Optional[int] = None, start_check: t.Union[int, float] = 0.5
    ) -> t.Tuple[str, bool]:
        """Pass."""
        current_run = self.current_run_duration_in_minutes

        if self.is_running:
            pre = f"Discover is running ({current_run} minutes so far)"

            if (
                isinstance(current_run, (int, float)) and isinstance(start_check, (int, float))
            ) and current_run <= start_check:
                return f"{pre} - started less than {start_check} minutes ago", False

            if self.is_correlation_finished:  # pragma: no cover
                return f"{pre} - correlation has finished", True

            return f"{pre} - correlation has NOT finished", False

        next_mins = self.next_run_starts_in_minutes
        reason = f"Discover is not running and next is in {next_mins} minutes"

        if isinstance(for_next_minutes, int):
            if self.next_run_within_minutes(for_next_minutes):
                return f"{reason} (less than {for_next_minutes} minutes)", False
            return f"{reason} (more than {for_next_minutes} minutes)", True

        return reason, True


class Dashboard(ModelMixins):
    """API for working with discovery lifecycle.

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
        return DiscoverData(
            raw=self._get().to_dict(), adapters=self.adapters.get(get_clients=False)
        )

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
            time.sleep(2)
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
            time.sleep(2)
        return self.get()

    def _get(self) -> json_api.lifecycle.Lifecycle:
        """Direct API method to get discovery cycle metadata."""
        api_endpoint = ApiEndpoints.lifecycle.get
        return api_endpoint.perform_request(http=self.auth.http)

    def _start(self) -> str:
        """Direct API method to start a discovery cycle."""
        api_endpoint = ApiEndpoints.lifecycle.start
        return api_endpoint.perform_request(http=self.auth.http)

    def _stop(self) -> str:
        """Direct API method to stop a discovery cycle."""
        api_endpoint = ApiEndpoints.lifecycle.stop
        return api_endpoint.perform_request(http=self.auth.http)

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        from ..adapters.adapters import Adapters

        self.adapters: Adapters = Adapters(auth=self.auth)
        """Work with adapters"""
