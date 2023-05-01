# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import types
import typing as t

import marshmallow
import marshmallow.fields as mm_fields


from ....constants import enforcements as enums
from ....http import Http
from ....tools import get_diff_seconds, listify
from ..base2 import BaseModel, BaseSchema
from ..custom_fields import SchemaBool, SchemaDatetime, SchemaObjectIDDatetime, field_from_mm
from .result import Result, ResultSchema
from .task_basic import TaskBasic
from .task_full import TaskFull


class TaskSchema(BaseSchema):
    """Schema for human friendly version of tasks for enforcements."""

    id = mm_fields.Int(data_key="id", description="The id of the task in the UI", required=True)
    uuid = mm_fields.Str(data_key="uuid", description="The uuid of the task", required=True)
    name = mm_fields.Str(data_key="name", description="The name of the task", required=True)
    enforcement_name = mm_fields.Str(
        data_key="enforcement_name", description="The name of the enforcement", required=True
    )
    enforcement_uuid = mm_fields.Str(
        data_key="enforcement_uuid", description="The uuid of the enforcement", required=True
    )

    query_type = mm_fields.Str(
        data_key="query_type",
        description="The type of the query",
        allow_none=True,
        load_default=None,
    )
    query_name = mm_fields.Str(
        data_key="query_name",
        description="The name of the query",
        allow_none=True,
        load_default=None,
    )
    query_uuid = mm_fields.Str(
        data_key="query_uuid",
        description="The uuid of the query",
        allow_none=True,
        load_default=None,
    )

    data_scope_uuid = mm_fields.Str(
        data_key="data_scope_uuid",
        description="The uuid of the data scope of the query, if any",
        allow_none=True,
        load_default=None,
    )
    discover_uuid = mm_fields.Str(
        data_key="discover_uuid",
        description="The uuid of the discover cycle that created this task, if any",
        allow_none=True,
        load_default=None,
    )

    schedule_method = mm_fields.Str(
        data_key="schedule_method",
        description="Method of scheduling",
        allow_none=True,
        load_default=None,
    )
    schedule_conditions = mm_fields.Str(
        data_key="schedule_conditions",
        description="The conditions of the schedule",
        allow_none=True,
        load_default=None,
    )
    schedule_period = mm_fields.Str(
        data_key="schedule_period",
        description="The period of the schedule",
        allow_none=True,
        load_default=None,
    )
    schedule_recurrence = mm_fields.Int(
        data_key="schedule_recurrence",
        description="The recurrence of the schedule",
        allow_none=True,
        load_default=None,
    )
    schedule_time = mm_fields.Str(
        data_key="schedule_time",
        description="The time of the schedule",
        allow_none=True,
        load_default=None,
    )

    only_against_new = SchemaBool(
        data_key="only_against_new",
        description="Only run against new assets",
        allow_none=True,
        load_default=None,
    )
    only_against_first_count = mm_fields.Int(
        data_key="only_against_first_count",
        description="Only run against the first N assets",
        allow_none=True,
        load_default=None,
    )
    only_when_above_count = mm_fields.Int(
        data_key="only_when_above_count",
        description="Only run when the asset count is above N",
        allow_none=True,
        load_default=None,
    )
    only_when_below_count = mm_fields.Int(
        data_key="only_when_below_count",
        description="Only run when the asset count is below N",
        allow_none=True,
        load_default=None,
    )
    only_when_count_decreases = SchemaBool(
        data_key="only_when_count_decreases",
        description="Only run when the asset count decreases",
        allow_none=True,
        load_default=None,
    )
    only_when_count_increases = SchemaBool(
        data_key="only_when_count_increases",
        description="Only run when the asset count increases",
        allow_none=True,
        load_default=None,
    )

    previous_count = mm_fields.Int(
        data_key="previous_count",
        description="The number of times task has been run",
        allow_none=True,
        load_default=None,
    )
    previous_at = SchemaDatetime(
        data_key="previous_at",
        description="The datetime of the last time the task was run",
        allow_none=True,
        load_default=None,
    )
    created_at = SchemaObjectIDDatetime(
        data_key="created_at",
        description="The datetime of the task creation",
        allow_none=True,
        load_default=None,
    )
    started_at = SchemaDatetime(
        data_key="started_at",
        description="The datetime of the task start",
        allow_none=True,
        load_default=None,
    )
    stopped_at = SchemaDatetime(
        data_key="stopped_at",
        description="The datetime of the task stop",
        allow_none=True,
        load_default=None,
    )
    duration_seconds = mm_fields.Float(
        data_key="duration_seconds",
        description="The duration of the task in seconds",
        allow_none=True,
        load_default=None,
    )

    total_count = mm_fields.Int(
        data_key="total_count",
        description="The total number of assets",
        allow_none=True,
        load_default=None,
    )
    success_count = mm_fields.Int(
        data_key="success_count",
        description="The number of assets that had no errors",
        allow_none=True,
        load_default=None,
    )
    failure_count = mm_fields.Int(
        data_key="failure_count",
        description="The number of assets that had errors",
        allow_none=True,
        load_default=None,
    )

    is_started = SchemaBool(
        data_key="is_started",
        description="Whether the task is started",
        allow_none=True,
        load_default=None,
    )
    is_stopped = SchemaBool(
        data_key="is_stopped",
        description="Whether the task is stopped",
        allow_none=True,
        load_default=None,
    )
    is_running = SchemaBool(
        data_key="is_running",
        description="Whether the task is running",
        allow_none=True,
        load_default=None,
    )
    is_error = SchemaBool(
        data_key="is_error",
        description="Whether the task finished with errors",
        allow_none=True,
        load_default=None,
    )
    is_success = SchemaBool(
        data_key="is_success",
        description="Whether the task finished without errors",
        allow_none=True,
        load_default=None,
    )
    is_terminated = SchemaBool(
        data_key="is_terminated",
        description="Whether the task is terminated",
        allow_none=True,
        load_default=None,
    )
    is_pending = SchemaBool(
        data_key="is_pending",
        description="Whether the task is pending",
        allow_none=True,
        load_default=None,
    )
    is_scheduled = SchemaBool(
        data_key="is_scheduled",
        description="Whether the task is a schedule",
        allow_none=True,
        load_default=None,
    )

    status = mm_fields.Str(
        data_key="status",
        description="The status of the task",
        allow_none=True,
        load_default=None,
    )
    status_results = mm_fields.Str(
        data_key="status_results",
        description="The aggregate status of the results for the task",
        allow_none=True,
        load_default=None,
    )

    results = mm_fields.List(
        mm_fields.Nested(ResultSchema()),
        data_key="results",
        description="The results of the task",
        allow_none=True,
        load_default=list,
    )

    @marshmallow.post_dump()
    def post_dump(self, data, **kwargs):
        """Post dump."""
        ret: t.Dict[str, t.Any] = {
            k.name: data.pop(k.name) for k in self.get_model_fields() if k.name in data
        }
        ret.update(data)
        return ret

    @staticmethod
    def get_model_cls() -> t.Any:
        """Return the model class this schema is for."""
        return Task

    class Meta:
        """Meta for TaskSchema."""

        type_: str = "PROTO_TASK"
        unknown: str = marshmallow.INCLUDE


SCHEMA: marshmallow.Schema = TaskSchema()


@dataclasses.dataclass(frozen=True)
class Task(BaseModel):
    """Model for human friendly version of tasks for enforcements."""

    http: Http = dataclasses.field(repr=False)

    id: int = field_from_mm(SCHEMA, "id")
    uuid: str = field_from_mm(SCHEMA, "uuid")
    name: str = field_from_mm(SCHEMA, "name")
    enforcement_name: str = field_from_mm(SCHEMA, "enforcement_name")
    enforcement_uuid: str = field_from_mm(SCHEMA, "enforcement_uuid")

    query_name: t.Optional[str] = field_from_mm(SCHEMA, "query_name")
    query_uuid: t.Optional[str] = field_from_mm(SCHEMA, "query_uuid")
    query_type: t.Optional[str] = field_from_mm(SCHEMA, "query_type")

    data_scope_uuid: t.Optional[str] = field_from_mm(SCHEMA, "data_scope_uuid")
    discover_uuid: t.Optional[str] = field_from_mm(SCHEMA, "discover_uuid")

    schedule_method: t.Optional[str] = field_from_mm(SCHEMA, "schedule_method")
    schedule_conditions: t.Optional[str] = field_from_mm(SCHEMA, "schedule_conditions")
    schedule_period: t.Optional[str] = field_from_mm(SCHEMA, "schedule_period")
    schedule_recurrence: t.Optional[int] = field_from_mm(SCHEMA, "schedule_recurrence")
    schedule_time: t.Optional[str] = field_from_mm(SCHEMA, "schedule_time")

    only_against_new: t.Optional[bool] = field_from_mm(SCHEMA, "only_against_new")
    only_against_first_count: t.Optional[int] = field_from_mm(SCHEMA, "only_against_first_count")
    only_when_above_count: t.Optional[int] = field_from_mm(SCHEMA, "only_when_above_count")
    only_when_below_count: t.Optional[int] = field_from_mm(SCHEMA, "only_when_below_count")
    only_when_count_decreases: t.Optional[bool] = field_from_mm(SCHEMA, "only_when_count_decreases")
    only_when_count_increases: t.Optional[bool] = field_from_mm(SCHEMA, "only_when_count_increases")

    previous_count: t.Optional[int] = field_from_mm(SCHEMA, "previous_count")
    previous_at: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "previous_at")
    created_at: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "created_at")
    started_at: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "started_at")
    stopped_at: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "stopped_at")
    duration_seconds: t.Optional[float] = field_from_mm(SCHEMA, "duration_seconds")

    total_count: t.Optional[int] = field_from_mm(SCHEMA, "total_count")
    success_count: t.Optional[int] = field_from_mm(SCHEMA, "success_count")
    failure_count: t.Optional[int] = field_from_mm(SCHEMA, "failure_count")

    is_started: t.Optional[bool] = field_from_mm(SCHEMA, "is_started")
    is_stopped: t.Optional[bool] = field_from_mm(SCHEMA, "is_stopped")
    is_running: t.Optional[bool] = field_from_mm(SCHEMA, "is_running")
    is_error: t.Optional[bool] = field_from_mm(SCHEMA, "is_error")
    is_success: t.Optional[bool] = field_from_mm(SCHEMA, "is_success")
    is_terminated: t.Optional[bool] = field_from_mm(SCHEMA, "is_terminated")
    is_pending: t.Optional[bool] = field_from_mm(SCHEMA, "is_pending")
    is_scheduled: t.Optional[bool] = field_from_mm(SCHEMA, "is_scheduled")

    status: t.Optional[str] = field_from_mm(SCHEMA, "status")
    status_results: t.Optional[str] = field_from_mm(SCHEMA, "status_results")

    results: t.List[Result] = field_from_mm(SCHEMA, "results")

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA
    ENUMS: t.ClassVar[types.ModuleType] = enums

    @property
    def action_types(self) -> t.List[str]:
        """Return all action types used by this task."""
        return [result.type for result in self.results]

    @property
    def result_main(self) -> t.Optional[Result]:
        """Return the result for the "main" workflow for this task."""
        for result in self.results:
            if result.flow_type == self.ENUMS.FlowTypes.main.value:
                return result

    @property
    def results_success(self) -> t.List[Result]:
        """Return the results for the "success" workflow for this task."""
        return [x for x in self.results if x.flow_type == self.ENUMS.FlowTypes.success.value]

    @property
    def results_failure(self) -> t.List[Result]:
        """Return the results for the "failure" workflow for this task."""
        return [x for x in self.results if x.flow_type == self.ENUMS.FlowTypes.failure.value]

    @property
    def results_post(self) -> t.List[Result]:
        """Return the results for the "post" workflow for this task."""
        return [x for x in self.results if x.flow_type == self.ENUMS.FlowTypes.post.value]

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get schema class for this model."""
        return TaskSchema

    @classmethod
    def load(
        cls, basic: t.Union[TaskBasic, dict], full: t.Union[TaskFull, dict], http: Http
    ) -> "Task":
        """Load a task from basic and full data.

        Args:
            basic (t.Union[TaskBasic, dict]): The basic task.
            full (tt.Union[TaskFull, dict]): The full task.
            http (Http): The HTTP client.

        Returns:
            Task: The loaded task.
        """
        data: dict = {"http": http, **cls.load_tasks(basic=basic, full=full)}
        task: Task = cls.SCHEMA.load(data)
        return task

    @classmethod
    def load_tasks(cls, basic: t.Union[TaskBasic, dict], full: t.Union[TaskFull, dict]) -> dict:
        """Compress a task in basic format and full format to a single view.

        Args:
            basic (t.Union[TaskBasic, dict]): The basic task.
            full (t.Union[TaskFull, dict]): The full task.

        Returns:
            dict: The compressed task.
        """
        _result: dict = full["result"]
        _meta: dict = _result.get("metadata") or {}
        _trigger: dict = _meta.get("trigger") or {}
        _conditions: dict = _trigger.get("conditions") or {}
        _view: dict = _trigger.get("view") or {}

        status: str = basic["result_metadata_status"]
        schedule_method: str = basic["scheduling"]
        failure_count: t.Optional[int] = basic["failure_count"]
        started_at: t.Optional[datetime.datetime] = basic["started_at"]
        stopped_at: t.Optional[datetime.datetime] = basic["finished_at"]
        duration_seconds: t.Optional[float] = get_diff_seconds(started_at, stopped_at)
        only_against_new: bool = cls.ENUMS.RunAgainst.is_against_new(_trigger.get("run_on", ""))
        is_stopped: bool = bool(stopped_at)
        is_started: bool = bool(started_at)
        is_running: bool = is_started and not is_stopped
        is_error: bool = bool(failure_count) or cls.ENUMS.StatusTask.is_error(status)
        is_success: bool = cls.ENUMS.StatusTask.is_success(status)
        is_terminated: bool = cls.ENUMS.StatusTask.is_terminated(status)
        is_pending: bool = cls.ENUMS.StatusTask.is_pending(status)
        is_scheduled: bool = cls.ENUMS.RunMethod.is_from_schedule(schedule_method)
        results: t.List[dict] = cls.load_results(basic=basic, full=full)

        task: dict = {
            "id": basic["pretty_id"],
            "uuid": basic["uuid"],
            "name": basic["result_metadata_task_name"],
            "enforcement_name": basic["enforcement_name"],
            "enforcement_uuid": full["enforcement_id"],
            "query_name": basic["result_metadata_trigger_view_name"],
            "query_uuid": _view.get("id"),
            "query_type": basic["module"],
            "data_scope_uuid": _meta.get("resource_scope_id"),
            "discover_uuid": basic["discovery_id"],
            "schedule_method": schedule_method,
            "schedule_conditions": basic["result_metadata_trigger_condition"],
            "schedule_period": _trigger.get("period", ""),
            "schedule_recurrence": _trigger.get("period_recurrence"),
            "schedule_time": _trigger.get("period_time"),
            "only_against_new": only_against_new,
            "only_against_first_count": _trigger.get("run_on_top_results"),
            "only_when_above_count": _conditions.get("above"),
            "only_when_below_count": _conditions.get("below"),
            "only_when_count_decreases": _conditions.get("previous_entities", False),
            "only_when_count_increases": _conditions.get("new_entities", False),
            "previous_count": _trigger.get("times_triggered"),
            "previous_at": _trigger.get("last_triggered"),
            "created_at": basic["date_fetched"],
            "started_at": started_at,
            "stopped_at": stopped_at,
            "duration_seconds": duration_seconds,
            "total_count": basic["affected_assets"],
            "success_count": basic["success_count"],
            "failure_count": failure_count,
            "status": status,
            "status_results": basic["aggregated_status"],
            "results": results,
            "is_scheduled": is_scheduled,
            "is_running": is_running,
            "is_stopped": is_stopped,
            "is_error": is_error,
            "is_success": is_success,
            "is_terminated": is_terminated,
            "is_started": is_started,
            "is_pending": is_pending,
        }
        return task

    @classmethod
    def load_results(
        cls, basic: t.Union[TaskBasic, dict], full: t.Union[TaskFull, dict]
    ) -> t.List[dict]:
        """Load the basic and full results into new result models.

        Args:
            basic (t.Union[TaskBasic, dict]): The basic task.
            full (t.Union[TaskFull, dict]): The full task.
        """
        basic_results: t.Dict[str, t.List[dict]] = basic["actions_details"]
        full_results: dict = full["result"]
        results: t.List[dict] = []

        for flow_type in cls.ENUMS.FlowTypes:
            basic_flow_results: t.List[dict] = listify(basic_results.get(flow_type.name, []))
            full_flow_results: t.List[dict] = listify(full_results.get(flow_type.name, []))
            flow_count = len(basic_flow_results)
            for flow_index, result_basic in enumerate(basic_flow_results):
                result: dict = cls.load_result(
                    flow_type=flow_type.name,
                    flow_index=flow_index,
                    flow_count=flow_count,
                    basic=result_basic,
                    full=full_flow_results[flow_index],
                )
                results.append(result)
        return results

    @classmethod
    def load_result(
        cls,
        flow_type: str,
        flow_index: int,
        flow_count: int,
        basic: dict,
        full: dict,
    ) -> dict:
        """Load a basic and full result into a new result model.

        Args:
            flow_type (str): The flow type.
            flow_index (int): The flow index.
            flow_count (int): The flow count.
            basic (dict): The basic result.
            full (dict): The full result.
        """
        _action: dict = full.get("action") or {}
        _ifttt: dict = full.get("ifttt") or {}

        started_at: t.Optional[str] = basic.get("start_date")
        stopped_at: t.Optional[str] = basic.get("end_date")
        duration_seconds: t.Optional[float] = get_diff_seconds(started_at, stopped_at)
        failure_count: t.Optional[int] = basic.get("unsuccessful_count")
        status: str = basic.get("status")
        is_started: bool = bool(started_at)
        is_stopped: bool = bool(stopped_at)
        is_running: bool = is_started and not is_stopped
        is_success: bool = cls.ENUMS.StatusResult.is_success(status)
        is_error: bool = bool(failure_count) or cls.ENUMS.StatusResult.is_error(status)
        is_terminated: bool = cls.ENUMS.StatusResult.is_terminated(status)
        is_pending: bool = cls.ENUMS.StatusResult.is_pending(status)

        result: dict = {
            "flow_type": flow_type,
            "flow_position": flow_index + 1,
            "flow_count": flow_count,
            "name": basic.get("action_name"),
            "uuid": _action.get("action_id"),
            "type": basic.get("name"),
            "category": _action.get("action_type"),
            "config": _action.get("config") or {},
            "ifttt": _ifttt.get("content"),
            "is_ifttt_enabled": _ifttt.get("include_output"),
            "started_at": started_at,
            "stopped_at": stopped_at,
            "duration_seconds": duration_seconds,
            "total_count": basic.get("total_affected"),
            "success_count": basic.get("successful_count"),
            "failure_count": failure_count,
            "message": basic.get("status_details"),
            "is_started": is_started,
            "is_stopped": is_stopped,
            "is_running": is_running,
            "is_success": is_success,
            "is_error": is_error,
            "is_terminated": is_terminated,
            "is_pending": is_pending,
            "status": status,
        }
        return result

    @staticmethod
    def _str_properties() -> t.List[str]:
        return [
            "name",
            "enforcement_name",
            "query_name",
            "query_type",
            "schedule_method",
            "schedule_conditions",
            "started_at",
            "stopped_at",
            "duration_seconds",
            "total_count",
            "success_count",
            "failure_count",
            "status",
            "status_results",
            "action_types",
        ]

    def __repr__(self):
        return self.__str__()
