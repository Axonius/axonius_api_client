# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import types
import typing as t

import marshmallow
import marshmallow.fields as mm_fields

from ....constants import enforcements as enums
from ..base2 import BaseModel, BaseSchema
from ..custom_fields import SchemaBool, SchemaDatetime, field_from_mm


class ResultSchema(BaseSchema):
    """Schema of result for an action in a flow_type of a task for an enforcement."""

    flow_type = mm_fields.Str(description="The type of flow of the result", required=True)
    flow_position = mm_fields.Int(
        description="The position of the result in the flow_type", required=True
    )
    flow_count = mm_fields.Int(
        description="The total number of results in the flow_type", required=True
    )

    name = mm_fields.Str(description="The name of the action", required=True)
    uuid = mm_fields.Str(description="The uuid of the action", required=True)
    type = mm_fields.Str(description="The type of the action", required=True)
    category = mm_fields.Str(
        description="The category of the action", allow_none=True, load_default=None
    )

    config = mm_fields.Dict(
        description="The config of the action", allow_none=True, load_default=dict
    )
    ifttt = mm_fields.Str(
        description="The if-this-then-that content for the action",
        allow_none=True,
        load_default=None,
    )
    is_ifttt_enabled = SchemaBool(
        description="Whether if-this-then-that is enabled", allow_none=True, load_default=None
    )

    started_at = SchemaDatetime(
        description="The time the action started", allow_none=True, load_default=None
    )
    stopped_at = SchemaDatetime(
        description="The time the action stopped", allow_none=True, load_default=None
    )
    duration_seconds = mm_fields.Float(
        description="The duration of the action in seconds", allow_none=True, load_default=None
    )

    total_count = mm_fields.Int(
        description="The total count of the action", allow_none=True, load_default=None
    )
    failure_count = mm_fields.Int(
        description="The failure count of the action", allow_none=True, load_default=None
    )
    success_count = mm_fields.Int(
        description="The success count of the action", allow_none=True, load_default=None
    )

    is_started = SchemaBool(
        data_key="is_started",
        description="Whether the action is started",
        allow_none=True,
        load_default=None,
    )
    is_stopped = SchemaBool(
        data_key="is_stopped",
        description="Whether the action is stopped",
        allow_none=True,
        load_default=None,
    )
    is_running = SchemaBool(
        data_key="is_running",
        description="Whether the action is running",
        allow_none=True,
        load_default=None,
    )
    is_error = SchemaBool(
        data_key="is_error",
        description="Whether the action finished with errors",
        allow_none=True,
        load_default=None,
    )
    is_success = SchemaBool(
        data_key="is_success",
        description="Whether the action finished without errors",
        allow_none=True,
        load_default=None,
    )
    is_terminated = SchemaBool(
        data_key="is_terminated",
        description="Whether the action is terminated",
        allow_none=True,
        load_default=None,
    )
    is_pending = SchemaBool(
        data_key="is_pending",
        description="Whether the action is pending",
        allow_none=True,
        load_default=None,
    )

    message = mm_fields.Str(
        description="The message of the action", allow_none=True, load_default=None
    )
    status = mm_fields.Str(
        description="The status of the action", allow_none=True, load_default=None
    )

    class Meta:
        """Meta."""

        type_ = "PROTO_TASK_RESULT"
        unknown = marshmallow.INCLUDE

    @staticmethod
    def get_model_cls() -> t.Any:
        """Return the model class this schema is for."""
        return Result


SCHEMA: marshmallow.Schema = ResultSchema()


@dataclasses.dataclass(frozen=True)
class Result(BaseModel):
    """Model of result for an action in a flow_type of a task for an enforcement."""

    flow_type: str = field_from_mm(SCHEMA, "flow_type")
    flow_position: int = field_from_mm(SCHEMA, "flow_position")
    flow_count: int = field_from_mm(SCHEMA, "flow_count")

    name: str = field_from_mm(SCHEMA, "name")
    uuid: str = field_from_mm(SCHEMA, "uuid")
    type: str = field_from_mm(SCHEMA, "type")
    category: t.Optional[str] = field_from_mm(SCHEMA, "category")

    config: dict = field_from_mm(SCHEMA, "config")
    ifttt: t.Optional[str] = field_from_mm(SCHEMA, "ifttt")
    is_ifttt_enabled: t.Optional[bool] = field_from_mm(SCHEMA, "is_ifttt_enabled")

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

    message: t.Optional[str] = field_from_mm(SCHEMA, "message")
    status: t.Optional[str] = field_from_mm(SCHEMA, "status")

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA
    ENUMS: t.ClassVar[types.ModuleType] = enums

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get schema class for this model."""
        return ResultSchema
