# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t
from datetime import datetime

from ....constants.enforcements import StatusResult, Workflow
from ....tools import coerce_bool, coerce_int, dt_parse, get_diff_seconds
from ..base import BaseModel
from ..custom_fields import desc_field
from .mixins import SerialMixins


@dataclasses.dataclass(frozen=True)
class Result(SerialMixins, BaseModel):
    """Model of result for an action in a workflow of a task for an enforcement."""

    workflow: str = desc_field("Workflow type for action")
    workflow_position: int = desc_field("Position of result within workflow")
    workflow_count: int = desc_field("Count of total results within workflow")

    action_name: t.Optional[str] = desc_field("Name of action", default=None)
    action_uuid: t.Optional[str] = desc_field("UUID of action", default=None)
    action_type: t.Optional[str] = desc_field("Type of action", default=None)
    action_category: t.Optional[str] = desc_field("Category of action", default=None)
    action_config: t.Optional[dict] = desc_field("Configuration of action", default_factory=dict)
    action_ifttt: t.Optional[str] = desc_field("Configuration of if-this-then-that", default=None)

    duration_seconds: t.Optional[float] = desc_field("Number of seconds action took to run", default=None)
    started_at: t.Optional[datetime] = desc_field("When action started", default=None)
    stopped_at: t.Optional[datetime] = desc_field("When action finished", default=None)

    failure_count: t.Optional[int] = desc_field("Count of assets with failure", default=None)
    success_count: t.Optional[int] = desc_field("Count of assets with success", default=None)
    total_count: t.Optional[int] = desc_field("Count of assets total", default=None)

    is_ifttt_enabled: t.Optional[bool] = desc_field("Is if-this-then-that enabled", default=None)
    is_running: t.Optional[bool] = desc_field("Is status=running", default=None)
    is_stopped: t.Optional[bool] = desc_field("Is stopped_at!=None", default=None)
    is_successful: t.Optional[bool] = desc_field("Is status=success", default=None)

    message: t.Optional[str] = desc_field("Message from action", default=None)
    status: t.Optional[str] = desc_field("Status of action", default=None)

    enum_status: t.ClassVar[StatusResult] = StatusResult
    """Enum for `status`."""

    enum_workflow: t.ClassVar[Workflow] = Workflow
    """Enum for `workflow`."""

    @classmethod
    def _csv_key(cls, key: str) -> str:
        """Build a key for use in CSV."""
        return f"result_{key}"

    @classmethod
    def load(cls, workflow: str, index: int, total: int, basic: dict, full: dict) -> "Result":
        """Create a Result object from a result for an action in a result of a basic task."""
        # basic attributes
        action_name: t.Optional[str] = basic.get("action_name")
        action_type: t.Optional[str] = basic.get("name")
        failure_count: t.Optional[int] = basic.get("unsuccessful_count")
        message: t.Optional[str] = basic.get("status_details")
        started_at: t.Optional[str] = basic.get("start_date")
        status: t.Optional[str] = basic.get("status")
        stopped_at: t.Optional[str] = basic.get("end_date")
        success_count: t.Optional[int] = basic.get("successful_count")
        total_count: t.Optional[int] = basic.get("total_affected")

        # full attributes, none of these are in basic
        _action: dict = full.get("action") or {}
        _ifttt: dict = full.get("ifttt") or {}
        action_category: t.Optional[str] = _action.get("action_type")
        action_config: dict = _action.get("config") or {}
        action_ifttt: t.Optional[str] = _ifttt.get("content")
        action_uuid: t.Optional[str] = _action.get("action_id")
        is_ifttt_enabled: t.Optional[bool] = _ifttt.get("enable")

        # coercions
        failure_count: t.Optional[int] = coerce_int(failure_count, allow_none=True)
        is_ifttt_enabled: t.Optional[bool] = coerce_bool(is_ifttt_enabled, allow_none=True)
        is_running: bool = cls.enum_status.running._enums_check(status)
        is_stopped: bool = bool(stopped_at)
        is_successful: bool = cls.enum_status.success._enums_check(status)
        started_at: t.Optional[datetime] = dt_parse(started_at, allow_none=True)
        stopped_at: t.Optional[datetime] = dt_parse(stopped_at, allow_none=True)
        success_count: t.Optional[int] = coerce_int(success_count, allow_none=True)
        total_count: t.Optional[int] = coerce_int(total_count, allow_none=True)
        workflow_position: int = index + 1
        duration_seconds: t.Optional[int] = get_diff_seconds(start=started_at, stop=stopped_at)

        ret: Result = cls(
            action_category=action_category,
            action_config=action_config,
            action_ifttt=action_ifttt,
            action_name=action_name,
            action_type=action_type,
            action_uuid=action_uuid,
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
