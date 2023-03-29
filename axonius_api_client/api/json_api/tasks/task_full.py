# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t
from datetime import datetime

import marshmallow

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaDatetime, get_schema_dc


class TaskFullSchema(BaseSchemaJson):
    """Schema for enforcement task in full model."""

    id = marshmallow.fields.Str()
    uuid = marshmallow.fields.Str(
        description="The task id",
    )
    period = marshmallow.fields.Str(
        description="The period scheduled for running the task",
    )
    result = marshmallow.fields.Dict(
        description="The Task results per Action",
    )
    enforcement = marshmallow.fields.Str(
        description="The enforcement name",
    )
    task_name = marshmallow.fields.Str(
        description="The task name",
    )
    view = marshmallow.fields.Str(
        description="The name of the query defined as the enforcement set trigger",
    )
    condition = marshmallow.fields.Str(
        description="The condition which triggered the run",
    )
    pretty_id = marshmallow.fields.Int(
        description="The Pretty task ID",
    )
    enforcement_id = marshmallow.fields.Str(
        description="The Enforcement set ID",
    )
    date_fetched = marshmallow.fields.Str(
        description="The date when the task was created",
    )
    started = SchemaDatetime(
        description="The timestamp when the task started running",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    finished = SchemaDatetime(
        description="The timestamp when the task finished running",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )

    class Meta:
        """Marshmallow JSONAPI meta class."""

        type_ = "tasks_details_schema"
        self_url = "/api/tasks/{id}"
        self_url_kwargs = {"id": "<id>"}
        self_url_many = "/api/tasks"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return TaskFull


@dataclasses.dataclass()
class TaskFull(BaseModel):
    """Model for enforcement task with full data."""

    id: str = get_schema_dc(
        schema=TaskFullSchema,
        key="id",
    )
    uuid: str = get_schema_dc(
        schema=TaskFullSchema,
        key="uuid",
    )
    date_fetched: str = get_schema_dc(
        schema=TaskFullSchema,
        key="date_fetched",
    )
    period: str = get_schema_dc(
        schema=TaskFullSchema,
        key="period",
    )
    enforcement: str = get_schema_dc(
        schema=TaskFullSchema,
        key="enforcement",
    )
    task_name: str = get_schema_dc(
        schema=TaskFullSchema,
        key="task_name",
    )
    view: str = get_schema_dc(
        schema=TaskFullSchema,
        key="view",
    )
    condition: str = get_schema_dc(
        schema=TaskFullSchema,
        key="condition",
    )
    pretty_id: str = get_schema_dc(
        schema=TaskFullSchema,
        key="pretty_id",
    )
    enforcement_id: str = get_schema_dc(
        schema=TaskFullSchema,
        key="enforcement_id",
    )
    result: dict = get_schema_dc(
        schema=TaskFullSchema,
        key="result",
    )
    finished: t.Optional[datetime] = get_schema_dc(
        schema=TaskFullSchema,
        key="finished",
        default=None,
    )
    started: t.Optional[datetime] = get_schema_dc(
        schema=TaskFullSchema,
        key="started",
        default=None,
    )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return TaskFullSchema
