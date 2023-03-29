# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t
from datetime import datetime

import marshmallow
import marshmallow_jsonapi

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaDatetime, get_schema_dc
from ..duration_operator import DurationOperator, DurationOperatorSchema
from ..resources import PaginationRequest, PaginationSchema


class GetTasksSchema(BaseSchemaJson):
    """Schema for getting enforcement tasks in basic model."""

    search = marshmallow.fields.Str(
        description="A textual value to search for",
        load_default="",
        dump_default="",
    )
    filter = marshmallow.fields.Str(
        description="AQL string, representing data filter",
        load_default="",
        dump_default="",
        allow_none=True,
    )
    history = SchemaDatetime(
        description="Historical date ISO formatted",
        allow_none=True,
    )
    sort = marshmallow.fields.Str(
        description="Field name to sort by with direction",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    page = marshmallow_jsonapi.fields.Nested(PaginationSchema)
    date_from = SchemaDatetime(
        description="The timestamp to filter from",
        allow_none=True,
    )
    date_to = SchemaDatetime(
        description="The timestamp to filter to",
        allow_none=True,
    )
    statuses_filter = marshmallow.fields.List(
        marshmallow.fields.Str(),
        description="List of task status to filter by",
        load_default=[],
        dump_default=[],
    )
    is_refresh = marshmallow.fields.Bool(
        description='Whether this request is made for "refresh" and should not be logged',
        load_default=False,
        dump_default=False,
    )
    action_names = marshmallow.fields.List(
        marshmallow.fields.Str(),
        description="List of task action names to filter by",
        load_default=[],
        dump_default=[],
    )
    enforcement_ids = marshmallow.fields.List(
        marshmallow.fields.Str(),
        description="List of task enforcement ids to filter by",
        load_default=[],
        dump_default=[],
    )
    aggregated_status = marshmallow.fields.List(
        marshmallow.fields.Str(),
        description="List of task results to filter by",
        load_default=[],
        dump_default=[],
    )
    task_id = marshmallow.fields.Integer(
        description="A specific task pretty id to filter by",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    discovery_cycle = marshmallow.fields.List(
        marshmallow.fields.Str(),
        description="List of  discovery ids to filter by",
        allow_none=True,
        load_default=[],
        dump_default=[],
    )
    duration_filter = DurationOperatorSchema()

    class Meta:
        """Marshmallow JSONAPI meta class."""

        type_ = "tasks_request_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return GetTasks


# TBD: .dataclass could be subclassed/replaced to generate attributes per the marshmallow schema
@dataclasses.dataclass()
class GetTasks(BaseModel):
    """Model for getting enforcement tasks in basic model."""

    # TBD: default could be grabbed from load_default/dump_default of marshmallow field
    search: t.Optional[str] = get_schema_dc(
        schema=GetTasksSchema,
        key="search",
        default="",
    )
    filter: t.Optional[str] = get_schema_dc(
        schema=GetTasksSchema,
        key="search",
        default="",
    )
    history: t.Optional[datetime] = get_schema_dc(
        schema=GetTasksSchema,
        key="history",
        default=None,
    )
    sort: t.Optional[str] = get_schema_dc(
        schema=GetTasksSchema,
        key="sort",
        default=None,
    )
    page: PaginationRequest = get_schema_dc(
        schema=GetTasksSchema,
        key="page",
        default_factory=PaginationRequest,
    )
    date_from: t.Optional[datetime] = get_schema_dc(
        schema=GetTasksSchema,
        key="date_from",
        default=None,
    )
    date_to: t.Optional[datetime] = get_schema_dc(
        schema=GetTasksSchema,
        key="date_to",
        default=None,
    )
    statuses_filter: t.List[str] = get_schema_dc(
        schema=GetTasksSchema,
        key="statuses_filter",
        default_factory=list,
    )
    is_refresh: bool = get_schema_dc(
        schema=GetTasksSchema,
        key="is_refresh",
        default=False,
    )
    action_names: t.List[str] = get_schema_dc(
        schema=GetTasksSchema,
        key="action_names",
        default_factory=list,
    )
    enforcement_ids: t.List[str] = get_schema_dc(
        schema=GetTasksSchema,
        key="enforcement_ids",
        default_factory=list,
    )
    aggregated_status: t.List[str] = get_schema_dc(
        schema=GetTasksSchema,
        key="aggregated_status",
        default_factory=list,
    )
    task_id: t.Optional[str] = get_schema_dc(
        schema=GetTasksSchema,
        key="task_id",
        default=None,
    )
    discovery_cycle: t.List[str] = get_schema_dc(
        schema=GetTasksSchema,
        key="discovery_cycle",
        default_factory=list,
    )
    duration_filter: DurationOperator = get_schema_dc(
        schema=GetTasksSchema,
        key="page",
        default_factory=DurationOperator,
    )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return GetTasksSchema
