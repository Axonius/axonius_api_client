# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaDatetime, field_from_mm


class TaskFullSchema(BaseSchemaJson):
    """Schema for enforcement task in full model."""

    id = mm_fields.Str(data_key="id", description="The task id", required=True)
    uuid = mm_fields.Str(data_key="uuid", description="The task id", required=True)
    pretty_id = mm_fields.Int(
        data_key="pretty_id", description="The task ID as it appears in the UI"
    )
    date_fetched = mm_fields.Str(
        data_key="date_fetched", description="The date when the task was created", required=True
    )
    enforcement = mm_fields.Str(
        data_key="enforcement", description="The enforcement name", required=True
    )
    enforcement_id = mm_fields.Str(
        data_key="enforcement_id", description="The Enforcement set ID", required=True
    )
    task_name = mm_fields.Str(data_key="task_name", description="The task name", required=True)
    result = mm_fields.Dict(
        data_key="result", description="The Task results per Action", load_default=dict
    )
    view = mm_fields.Str(
        data_key="view",
        description="The name of the query defined as the enforcement set trigger",
        allow_none=True,
        load_default=None,
    )
    period = mm_fields.Str(
        data_key="period",
        description="The period scheduled for running the task",
        allow_none=True,
        load_default=None,
    )
    condition = mm_fields.Str(
        data_key="condition",
        description="The condition which triggered the run",
        allow_none=True,
        load_default=None,
    )
    started = SchemaDatetime(
        data_key="started",
        description="The timestamp when the task started running",
        allow_none=True,
        load_default=None,
    )
    finished = SchemaDatetime(
        data_key="finished",
        description="The timestamp when the task finished running",
        allow_none=True,
        load_default=None,
    )

    class Meta:
        """Marshmallow JSONAPI metaclass."""

        type_: str = "tasks_details_schema"
        self_url: str = "/api/tasks/{id}"
        self_url_kwargs: t.Dict[str, str] = {"id": "<id>"}
        self_url_many: str = "/api/tasks"
        unknown: str = marshmallow.INCLUDE

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return TaskFull


SCHEMA: marshmallow.Schema = TaskFullSchema()


@dataclasses.dataclass()
class TaskFull(BaseModel):
    """Model for enforcement task with full data."""

    id: str = field_from_mm(SCHEMA, "id")
    uuid: str = field_from_mm(SCHEMA, "uuid")
    pretty_id: str = field_from_mm(SCHEMA, "pretty_id")
    date_fetched: str = field_from_mm(SCHEMA, "date_fetched")
    enforcement: str = field_from_mm(SCHEMA, "enforcement")
    enforcement_id: str = field_from_mm(SCHEMA, "enforcement_id")
    task_name: str = field_from_mm(SCHEMA, "task_name")

    result: dict = field_from_mm(SCHEMA, "result")

    view: t.Optional[str] = field_from_mm(SCHEMA, "view")
    period: t.Optional[str] = field_from_mm(SCHEMA, "period")
    condition: t.Optional[str] = field_from_mm(SCHEMA, "condition")
    started: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "started")
    finished: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "finished")

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return TaskFullSchema
