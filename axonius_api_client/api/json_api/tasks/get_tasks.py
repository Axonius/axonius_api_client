# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t
import datetime

import marshmallow

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaDatetime, field_from_mm
from ..duration_operator import DurationOperator, DurationOperatorSchema
from ..resources import PaginationRequest, PaginationSchema


class GetTasksSchema(BaseSchemaJson):
    """Schema for getting enforcement tasks in basic model."""

    search = marshmallow.fields.Str(
        data_key="search",
        description="A textual value to search for",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    filter = marshmallow.fields.Str(
        data_key="filter",
        description="AQL string, representing data filter",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    sort = marshmallow.fields.Str(
        data_key="sort",
        description="Field name to sort by with direction",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    history = SchemaDatetime(
        data_key="history",
        description="Historical date ISO formatted",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    date_from = SchemaDatetime(
        data_key="date_from",
        description="The timestamp to filter from",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    date_to = SchemaDatetime(
        data_key="date_to",
        description="The timestamp to filter to",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    task_id = marshmallow.fields.Integer(
        data_key="task_id",
        description="A specific task pretty id to filter by",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    statuses_filter = marshmallow.fields.List(
        marshmallow.fields.Str(),
        data_key="statuses_filter",
        description="List of task status to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    action_names = marshmallow.fields.List(
        marshmallow.fields.Str(),
        data_key="action_names",
        description="List of task action names to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    enforcement_ids = marshmallow.fields.List(
        marshmallow.fields.Str(),
        data_key="enforcement_ids",
        description="List of task enforcement ids to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    aggregated_status = marshmallow.fields.List(
        marshmallow.fields.Str(),
        data_key="aggregated_status",
        description="List of task results to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    discovery_cycle = marshmallow.fields.List(
        marshmallow.fields.Str(),
        data_key="discovery_cycle",
        description="List of  discovery ids to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    is_refresh = marshmallow.fields.Bool(
        data_key="is_refresh",
        description='Whether this request is made for "refresh" and should not be logged',
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    duration_filter = marshmallow.fields.Nested(
        DurationOperatorSchema(),
        data_key="duration_filter",
        description="Duration filter",
        allow_none=True,
        load_default=DurationOperator,
        dump_default=DurationOperator,
    )
    page = marshmallow.fields.Nested(
        PaginationSchema(),
        data_key="page",
        description="Pagination request",
        allow_none=True,
        load_default=PaginationRequest,
        dump_default=PaginationRequest,
    )

    class Meta:
        """Marshmallow JSONAPI metaclass."""

        type_ = "tasks_request_schema"
        unknown: str = marshmallow.INCLUDE

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return GetTasks


SCHEMA: marshmallow.Schema = GetTasksSchema()


@dataclasses.dataclass()
class GetTasks(BaseModel):
    """Model for getting enforcement tasks in basic model."""

    search: t.Optional[str] = field_from_mm(SCHEMA, "search")
    filter: t.Optional[str] = field_from_mm(SCHEMA, "filter")
    sort: t.Optional[str] = field_from_mm(SCHEMA, "sort")
    history: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "history")

    date_from: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "date_from")
    date_to: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "date_to")
    task_id: t.Optional[str] = field_from_mm(SCHEMA, "task_id")
    statuses_filter: t.Optional[t.List[str]] = field_from_mm(SCHEMA, "statuses_filter")
    action_names: t.Optional[t.List[str]] = field_from_mm(SCHEMA, "action_names")
    enforcement_ids: t.Optional[t.List[str]] = field_from_mm(SCHEMA, "enforcement_ids")
    aggregated_status: t.Optional[t.List[str]] = field_from_mm(SCHEMA, "aggregated_status")
    discovery_cycle: t.Optional[t.List[str]] = field_from_mm(SCHEMA, "discovery_cycle")
    is_refresh: t.Optional[bool] = field_from_mm(SCHEMA, "is_refresh")
    duration_filter: t.Optional[DurationOperator] = field_from_mm(SCHEMA, "duration_filter")
    page: t.Optional[PaginationRequest] = field_from_mm(SCHEMA, "page")

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return GetTasksSchema

    def __post_init__(self):
        """Post init."""
        if not isinstance(self.search, str):
            self.search = None
        if not isinstance(self.filter, str):
            self.filter = None
        if not isinstance(self.sort, str):
            self.sort = None

        if not isinstance(self.history, datetime.datetime):
            self.history = None
        if not isinstance(self.date_from, datetime.datetime):
            self.date_from = None
        if not isinstance(self.date_to, datetime.datetime):
            self.date_to = None

        if not isinstance(self.task_id, str):
            self.task_id = None
        if not isinstance(self.is_refresh, bool):
            self.is_refresh = None

        if not isinstance(self.statuses_filter, list):
            self.statuses_filter = []
        if not isinstance(self.action_names, list):
            self.action_names = []
        if not isinstance(self.enforcement_ids, list):
            self.enforcement_ids = []
        if not isinstance(self.aggregated_status, list):
            self.aggregated_status = []
        if not isinstance(self.discovery_cycle, list):
            self.discovery_cycle = []

        if not isinstance(self.page, PaginationRequest):
            self.page = PaginationRequest()
        if not isinstance(self.duration_filter, DurationOperator):
            self.duration_filter = DurationOperator()
