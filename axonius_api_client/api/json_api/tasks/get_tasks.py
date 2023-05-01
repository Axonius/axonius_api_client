# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..count_operator import OperatorTypes, TypeOperator, coerce_operator
from ..custom_fields import SchemaDatetime, field_from_mm
from ..duration_operator import DurationOperator, DurationOperatorSchema
from ..resources import PaginationRequest, PaginationSchema
from .task_filters import TaskFilters
from ....constants.ctypes import TypeDate, TypeDelta, TypeFloat, TypeMatch, TypeInt
from ....tools import coerce_date_delta, coerce_seconds, coerce_bool, dt_parse


class GetTasksSchema(BaseSchemaJson):
    """Schema for getting enforcement tasks in basic model."""

    search = mm_fields.Str(
        data_key="search",
        description="A textual value to search for",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    filter = mm_fields.Str(
        data_key="filter",
        description="AQL string data filter",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    sort = mm_fields.Str(
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
    task_id = mm_fields.Integer(
        data_key="task_id",
        description="A specific task pretty id to filter by",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    statuses_filter = mm_fields.List(
        mm_fields.Str(),
        data_key="statuses_filter",
        description="List of task status to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    action_names = mm_fields.List(
        mm_fields.Str(),
        data_key="action_names",
        description="List of task action names to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    enforcement_ids = mm_fields.List(
        mm_fields.Str(),
        data_key="enforcement_ids",
        description="List of task enforcement ids to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    aggregated_status = mm_fields.List(
        mm_fields.Str(),
        data_key="aggregated_status",
        description="List of task results to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    discovery_cycle = mm_fields.List(
        mm_fields.Str(),
        data_key="discovery_cycle",
        description="List of  discovery ids to filter by",
        allow_none=True,
        load_default=list,
        dump_default=list,
    )
    is_refresh = mm_fields.Bool(
        data_key="is_refresh",
        description='Whether this request is made for "refresh" and should not be logged',
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    duration_filter = mm_fields.Nested(
        DurationOperatorSchema(),
        data_key="duration_filter",
        description="Duration filter",
        allow_none=True,
        load_default=DurationOperator,
        dump_default=DurationOperator,
    )
    page = mm_fields.Nested(
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

    task_id: t.Optional[str] = field_from_mm(SCHEMA, "task_id")

    date_from: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "date_from")
    date_to: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "date_to")

    statuses_filter: t.Optional[t.List[str]] = field_from_mm(SCHEMA, "statuses_filter")
    action_names: t.Optional[t.List[str]] = field_from_mm(SCHEMA, "action_names")
    enforcement_ids: t.Optional[t.List[str]] = field_from_mm(SCHEMA, "enforcement_ids")
    aggregated_status: t.Optional[t.List[str]] = field_from_mm(SCHEMA, "aggregated_status")
    discovery_cycle: t.Optional[t.List[str]] = field_from_mm(SCHEMA, "discovery_cycle")

    is_refresh: t.Optional[bool] = field_from_mm(SCHEMA, "is_refresh")

    duration_filter: t.Optional[DurationOperator] = field_from_mm(SCHEMA, "duration_filter")
    page: t.Optional[PaginationRequest] = field_from_mm(SCHEMA, "page")

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA
    TASK_FILTERS: t.ClassVar[t.Optional[TaskFilters]] = None

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return GetTasksSchema

    def get_filters(self, task_filters: t.Optional[TaskFilters] = None) -> TaskFilters:
        """Pass."""
        if isinstance(task_filters, TaskFilters):
            return task_filters
        if not isinstance(self.TASK_FILTERS, TaskFilters):
            # noinspection PyUnresolvedReferences
            self.TASK_FILTERS = self.HTTP.CLIENT.enforcements.tasks.get_filters()
        return self.TASK_FILTERS

    def set_task_id(
        self, value: t.Optional[TypeInt] = None, task_filters: t.Optional[TaskFilters] = None
    ) -> t.Optional[int]:
        """Set the task id to filter results by.

        Args:
            value: The task id to filter by.
            task_filters: The task filters to use to validate the task id.
        """
        task_filters = self.get_filters(task_filters=task_filters)
        self.task_id = task_filters.check_task_id(value=value)
        return self.task_id

    def set_action_types(
        self,
        values: t.Optional[TypeMatch] = None,
        task_filters: t.Optional[TaskFilters] = None,
        **kwargs,
    ) -> t.List[str]:
        """Set the action types to filter results by.

        Args:
            values: The action types to filter by.
            task_filters: The task filters to use to validate the task id.
            **kwargs: Passed to :meth:`TaskFilters.check_action_types`

        Returns:
            The parsed list of action types that were set to `action_names`
        """
        task_filters = self.get_filters(task_filters=task_filters)
        self.action_names = task_filters.check_action_types(values=values, **kwargs)
        return self.action_names

    def set_discovery_uuids(
        self,
        values: t.Optional[TypeMatch] = None,
        task_filters: t.Optional[TaskFilters] = None,
        **kwargs,
    ) -> t.List[str]:
        """Set the discovery uuids to filter results by.

        Args:
            values: The discovery uuids to filter by (use re_prefix to treat as regex)
            task_filters: The task filters to use to validate the task id.
            **kwargs: Passed to :meth:`TaskFilters.check_discovery_uuids`

        Returns:
            The parsed list of discovery uuids that were set to `discovery_cycle`
        """
        task_filters = self.get_filters(task_filters=task_filters)
        self.discovery_cycle = task_filters.check_discovery_uuids(values=values, **kwargs)
        return self.discovery_cycle

    def set_enforcement_names(
        self,
        values: t.Optional[TypeMatch] = None,
        task_filters: t.Optional[TaskFilters] = None,
        **kwargs,
    ) -> t.List[str]:
        """Set the task UUIDs to filter results by enforcement names.

        Args:
            values: The enforcement names to filter by.
            task_filters: The task filters to use to validate the task id.
            **kwargs: Passed to :meth:`TaskFilters.check_enforcement_names`

        Returns:
            The parsed list of task UUIDs that were set to `enforcement_ids`
        """
        task_filters = self.get_filters(task_filters=task_filters)
        self.enforcement_ids = task_filters.check_enforcement_names(values=values, **kwargs)
        return self.enforcement_ids

    def set_statuses(
        self,
        values: t.Optional[TypeMatch] = None,
        task_filters: t.Optional[TaskFilters] = None,
        **kwargs,
    ) -> t.List[str]:
        """Set the task statuses to filter results by.

        Args:
            values: The statuses to filter by.
            task_filters: The task filters to use to validate the task id.
            **kwargs: Passed to :meth:`TaskFilters.check_statuses`

        Returns:
            The parsed list of statuses that were set to `statuses_filter`
        """
        task_filters = self.get_filters(task_filters=task_filters)
        self.statuses_filter = task_filters.check_statuses(values=values, **kwargs)
        return self.statuses_filter

    def set_statuses_result(
        self,
        values: t.Optional[TypeMatch] = None,
        task_filters: t.Optional[TaskFilters] = None,
        **kwargs,
    ) -> t.List[str]:
        """Set the task result statuses to filter results by.

        Args:
            values: The results statuses to filter by.
            task_filters: The task filters to use to validate the task id.
            **kwargs: Passed to :meth:`TaskFilters.check_statuses`

        Returns:
            The parsed list of results statuses that were set to `aggregated_status`
        """
        task_filters = self.get_filters(task_filters=task_filters)
        self.aggregated_status = task_filters.check_statuses(values=values, **kwargs)
        return self.aggregated_status

    def set_is_refresh(self, value: t.Optional[bool] = None) -> t.Optional[bool]:
        """Set the is_refresh to filter results by.

        Args:
            value: The is_refresh to filter by.

        Returns:
            The parsed value that was set to `is_refresh`
        """
        self.is_refresh = coerce_bool(value, allow_none=True)
        return self.is_refresh

    def set_date_from(
        self,
        value: t.Optional[TypeDate] = None,
        add: t.Optional[TypeDelta] = None,
        subtract: t.Optional[TypeDelta] = None,
    ) -> t.Optional[datetime.datetime]:
        """Set the date_from to filter results by.

        Args:
            value: The date_from to filter by.
            add: Seconds to add to parsed value (if no value, add to now).
            subtract: Seconds to subtract from parsed value (if no value, subtract from now).

        Returns:
            The parsed value that was set to `date_from`
        """
        self.date_from = coerce_date_delta(value=value, add=add, subtract=subtract)
        return self.date_from

    def set_date_to(
        self,
        value: t.Optional[TypeDate] = None,
        add: t.Optional[TypeDelta] = None,
        subtract: t.Optional[TypeDelta] = None,
    ) -> t.Optional[datetime.datetime]:
        """Set the date_to to filter results by.

        Args:
            value: The date_to to filter by.
            add: Seconds to add to parsed value (if no value, add to now).
            subtract: Seconds to subtract from parsed value (if no value, subtract from now).

        Returns:
            The parsed value that was set to `date_to`
        """
        self.date_to = coerce_date_delta(value=value, add=add, subtract=subtract)
        return self.date_to

    def set_history(self, value: t.Optional[TypeDate] = None) -> t.Optional[datetime.datetime]:
        """Set the history to filter results by.

        Args:
            value: The history to filter by.

        Returns:
            The parsed value that was set to `history`
        """
        self.history = dt_parse(value, allow_none=True)
        return self.history

    def set_duration(
        self,
        seconds: t.Optional[TypeFloat] = None,
        operator: t.Union[TypeOperator] = OperatorTypes.less.name,
    ) -> DurationOperator:
        """Only get tasks that have a duration that matches the operator and seconds.

        Args:
            seconds: The duration to filter by.
            operator: The operator to use to compare the duration.

        Returns:
            The parsed value that was set to `duration_filter`
        """
        seconds_float = coerce_seconds(seconds)
        operator = coerce_operator(operator)
        self.duration_filter = DurationOperator(type=operator, seconds_float=seconds_float)
        return self.duration_filter
