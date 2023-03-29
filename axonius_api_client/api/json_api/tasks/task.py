# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import bson

from ....constants.enforcements import RunCondition, RunMethod, StatusResult, StatusTask, Workflow
from ....tools import coerce_bool, coerce_int, dt_parse, get_diff_seconds, listify
from ..base import BaseModel
from .mixins import SerialMixins
from .task_basic import TaskBasic
from .task_full import TaskFull


@dataclasses.dataclass(frozen=True)
class Result(SerialMixins, BaseModel):
    """Model of result for an action in a workflow of a task for an enforcement."""

    workflow: str
    workflow_position: int
    workflow_count: int

    name: t.Optional[str] = None
    uuid: t.Optional[str] = None
    type: t.Optional[str] = None
    category: t.Optional[str] = None
    config: t.Optional[dict] = None
    ifttt: t.Optional[str] = None

    started_at: t.Optional[datetime.datetime] = None
    stopped_at: t.Optional[datetime.datetime] = None
    duration_seconds: t.Optional[float] = None

    total_count: t.Optional[int] = None
    failure_count: t.Optional[int] = None
    success_count: t.Optional[int] = None

    is_ifttt_enabled: t.Optional[bool] = None
    is_running: t.Optional[bool] = None
    is_stopped: t.Optional[bool] = None
    is_successful: t.Optional[bool] = None

    message: t.Optional[str] = None
    status: t.Optional[str] = None

    enum_status: t.ClassVar[StatusResult] = StatusResult
    """Enum for status."""

    enum_workflow: t.ClassVar[Workflow] = Workflow
    """Enum for workflow."""

    @classmethod
    def load(cls, workflow: str, index: int, total: int, basic: dict, full: dict) -> "Result":
        """Create a Result object from a result for an action in a result of a basic task."""
        # basic attributes
        name: t.Optional[str] = basic.get("action_name")
        type: t.Optional[str] = basic.get("name")
        failure_count: t.Optional[int] = basic.get("unsuccessful_count")
        message: t.Optional[str] = basic.get("status_details")
        started_at: t.Optional[str] = basic.get("start_date")
        status: t.Optional[str] = basic.get("status")
        stopped_at: t.Optional[str] = basic.get("end_date")
        success_count: t.Optional[int] = basic.get("successful_count")
        total_count: t.Optional[int] = basic.get("total_affected")

        # full complex references
        _action: dict = full.get("action") or {}
        _ifttt: dict = full.get("ifttt") or {}

        # full attributes, none of these are in basic
        category: t.Optional[str] = _action.get("type")
        config: dict = _action.get("config") or {}
        ifttt: t.Optional[str] = _ifttt.get("content")
        uuid: t.Optional[str] = _action.get("action_id")
        is_ifttt_enabled: t.Optional[bool] = _ifttt.get("enable")

        # coercions
        failure_count: t.Optional[int] = coerce_int(failure_count, allow_none=True)
        is_ifttt_enabled: t.Optional[bool] = coerce_bool(is_ifttt_enabled, allow_none=True)
        is_running: bool = cls.enum_status.running._enums_check(status)
        is_stopped: bool = bool(stopped_at)
        is_successful: bool = cls.enum_status.success._enums_check(status)
        started_at: t.Optional[datetime.datetime] = dt_parse(started_at, allow_none=True)
        stopped_at: t.Optional[datetime.datetime] = dt_parse(stopped_at, allow_none=True)
        success_count: t.Optional[int] = coerce_int(success_count, allow_none=True)
        total_count: t.Optional[int] = coerce_int(total_count, allow_none=True)
        workflow_position: int = index + 1
        duration_seconds: t.Optional[int] = get_diff_seconds(start=started_at, stop=stopped_at)

        ret: Result = cls(
            category=category,
            config=config,
            ifttt=ifttt,
            name=name,
            type=type,
            uuid=uuid,
            failure_count=failure_count,
            duration_seconds=duration_seconds,
            success_count=success_count,
            total_count=total_count,
            workflow_position=workflow_position,
            workflow_count=total,
            started_at=started_at,
            stopped_at=stopped_at,
            is_ifttt_enabled=is_ifttt_enabled,
            is_running=is_running,
            is_stopped=is_stopped,
            is_successful=is_successful,
            message=message,
            status=status,
            workflow=workflow,
        )
        return ret


@dataclasses.dataclass(frozen=True)
class Task(SerialMixins, BaseModel):
    """Human friendly model of tasks for enforcements."""

    id: int = None
    uuid: str = None
    name: str = None

    enforcement_name: str = None
    enforcement_uuid: str = None

    query_name: t.Optional[str] = None
    query_type: t.Optional[str] = None
    query_uuid: t.Optional[str] = None
    query_scope_uuid: t.Optional[str] = None
    discover_uuid: t.Optional[str] = None

    conditions: t.Optional[str] = None
    schedule_period: t.Optional[str] = None
    schedule_recurrence: t.Optional[int] = None
    schedule_time: t.Optional[str] = None

    only_against_count: t.Optional[int] = None
    only_against_new: t.Optional[bool] = None
    only_when_above_count: t.Optional[int] = None
    only_when_below_count: t.Optional[int] = None
    only_when_count_decreases: t.Optional[bool] = None
    only_when_count_increases: t.Optional[bool] = None

    previous_count: t.Optional[int] = None
    previous_at: t.Optional[datetime.datetime] = None

    created_at: t.Optional[datetime.datetime] = None
    started_at: t.Optional[datetime.datetime] = None
    stopped_at: t.Optional[datetime.datetime] = None
    duration_seconds: t.Optional[float] = None

    total_count: t.Optional[int] = None
    success_count: t.Optional[int] = None
    failure_count: t.Optional[int] = None

    is_scheduled: t.Optional[bool] = None
    is_running: t.Optional[bool] = None
    is_stopped: t.Optional[bool] = None
    is_successful: t.Optional[bool] = None

    status: t.Optional[str] = None
    status_results: t.Optional[str] = None
    result_count: t.Optional[int] = None
    results: t.Optional[t.List[Result]] = None

    enum_run_method: t.ClassVar[RunMethod] = RunMethod
    """Enum for run_method."""

    enum_run_condition: t.ClassVar[RunCondition] = RunCondition
    """Enum for run_condition."""

    enum_status: t.ClassVar[StatusTask] = StatusTask
    """Enum for status."""

    enum_status_results: t.ClassVar[StatusResult] = StatusResult
    """Enum for status_results."""

    @classmethod
    def _load_results(cls, basic: TaskBasic, full: TaskFull) -> t.Generator[Result, None, None]:
        """Load the results found in basic and full models into Result objects."""
        results_basic: t.Dict[str, t.List[dict]] = basic.actions_details
        results_full: dict = full.result

        for workflow in Workflow:
            workflow_results_basic: t.List[dict] = listify(results_basic.get(workflow.name, []))
            workflow_results_full: t.List[dict] = listify(results_full.get(workflow.name, []))
            total = len(workflow_results_basic)
            for index, result_basic in enumerate(workflow_results_basic):
                result_full: dict = workflow_results_full[index]
                yield Result.load(
                    index=index,
                    total=total,
                    workflow=workflow.name,
                    basic=result_basic,
                    full=result_full,
                )

    @classmethod
    def load(cls, basic: TaskBasic) -> "Task":
        """Create Task object from a TaskBasic."""
        # basic attributes
        id: str = basic.pretty_id
        uuid: str = basic.uuid
        name: str = basic.result_metadata_task_name
        enforcement_name: str = basic.enforcement_name
        query_name: str = basic.result_metadata_trigger_view_name
        query_type: str = basic.module
        conditions: str = basic.result_metadata_trigger_condition
        status: str = basic.result_metadata_status
        status_results: str = basic.aggregated_status
        total_count: int = basic.affected_assets
        success_count: int = basic.success_count
        failure_count: int = basic.failure_count
        is_scheduled: str = basic.scheduling
        created_at: str = basic.date_fetched
        started_at: t.Optional[datetime.datetime] = basic.started_at
        stopped_at: t.Optional[datetime.datetime] = basic.finished_at
        discover_uuid: t.Optional[str] = basic.discovery_id

        # have to get full model to get info hidden deep many nested layers of objects
        # XXX ensure cached!
        full: TaskFull = basic.get_full()

        # full complex references
        _metadata: dict = full.result.get("metadata") or {}
        _trigger: dict = _metadata.get("trigger") or {}
        _conditions: dict = _trigger.get("conditions") or {}
        _view: dict = _trigger.get("view") or {}

        # full attributes
        enforcement_uuid: str = full.enforcement_id
        only_against_count: t.Optional[int] = _trigger.get("run_on_top_results")
        only_against_new: t.Optional[str] = _trigger.get("run_on", "")
        only_when_above_count: t.Optional[int] = _conditions.get("above")
        only_when_below_count: t.Optional[int] = _conditions.get("below")
        only_when_count_decreases: t.Optional[bool] = _conditions.get("previous_entities", False)
        only_when_count_increases: t.Optional[bool] = _conditions.get("new_entities", False)
        previous_at: t.Optional[str] = _trigger.get("last_triggered")
        query_scope_uuid: t.Optional[str] = _metadata.get("resource_scope_id")
        query_uuid: t.Optional[str] = _view.get("id")
        previous_count: t.Optional[int] = _trigger.get("times_triggered")
        schedule_period: t.Optional[str] = _trigger.get("period", "")
        schedule_recurrence: t.Optional[int] = _trigger.get("period_recurrence")
        schedule_time: t.Optional[str] = _trigger.get("period_time")

        # coercions
        id: str = int(id)
        created_at: datetime.datetime = dt_parse(bson.ObjectId(created_at).generation_time)
        is_running: bool = cls.enum_status.running._enums_check(status)
        is_scheduled: bool = cls.enum_run_method.scheduled._enums_check(is_scheduled)
        is_stopped: bool = bool(stopped_at)
        is_successful: bool = cls.enum_status.success._enums_check(status)
        only_against_count: t.Optional[int] = coerce_int(only_against_count, allow_none=True)
        only_against_new: bool = only_against_new == "AllEntities"
        only_when_above_count: t.Optional[int] = coerce_int(only_when_above_count, allow_none=True)
        only_when_below_count: t.Optional[int] = coerce_int(only_when_below_count, allow_none=True)
        only_when_count_decreases: t.Optional[bool] = coerce_bool(
            only_when_count_decreases, allow_none=True
        )
        only_when_count_increases: t.Optional[bool] = coerce_bool(
            only_when_count_increases, allow_none=True
        )
        previous_at: t.Optional[datetime.datetime] = dt_parse(previous_at, allow_none=True)
        previous_count: t.Optional[int] = coerce_int(previous_count, allow_none=True)
        duration_seconds: t.Optional[float] = get_diff_seconds(start=started_at, stop=stopped_at)
        results: t.List[Result] = list(cls._load_results(basic=basic, full=full))
        result_count: int = len(results)

        ret: Task = cls(
            conditions=conditions,
            created_at=created_at,
            discover_uuid=discover_uuid,
            duration_seconds=duration_seconds,
            enforcement_name=enforcement_name,
            enforcement_uuid=enforcement_uuid,
            failure_count=failure_count,
            id=id,
            is_running=is_running,
            is_scheduled=is_scheduled,
            is_stopped=is_stopped,
            is_successful=is_successful,
            name=name,
            only_against_count=only_against_count,
            only_against_new=only_against_new,
            only_when_above_count=only_when_above_count,
            only_when_below_count=only_when_below_count,
            only_when_count_decreases=only_when_count_decreases,
            only_when_count_increases=only_when_count_increases,
            previous_at=previous_at,
            previous_count=previous_count,
            query_name=query_name,
            query_scope_uuid=query_scope_uuid,
            query_type=query_type,
            query_uuid=query_uuid,
            result_count=result_count,
            results=results,
            schedule_period=schedule_period,
            schedule_recurrence=schedule_recurrence,
            schedule_time=schedule_time,
            started_at=started_at,
            status=status,
            status_results=status_results,
            stopped_at=stopped_at,
            success_count=success_count,
            total_count=total_count,
            uuid=uuid,
        )
        return ret
