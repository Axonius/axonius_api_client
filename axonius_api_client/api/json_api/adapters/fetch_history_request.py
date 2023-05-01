# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields

from ....exceptions import ApiError, NotFoundError
from ....tools import coerce_bool
from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, field_from_mm
from ..resources import PaginationRequest, PaginationSchema
from ..time_range import TimeRange, TimeRangeSchema, UnitTypes
from .fetch_history_filters_response import AdapterFetchHistoryFilters
from .fetch_history_response import AdapterFetchHistorySchema


class AdapterFetchHistoryRequestSchema(BaseSchemaJson):
    """Schema for requesting fetch history."""

    adapters_filter = mm_fields.List(
        mm_fields.Str(),
        load_default=list,
        dump_default=list,
    )
    connection_labels_filter = mm_fields.List(
        mm_fields.Str(),
        load_default=list,
        dump_default=list,
    )
    clients_filter = mm_fields.List(
        mm_fields.Str(),
        load_default=list,
        dump_default=list,
    )
    statuses_filter = mm_fields.List(
        mm_fields.Str(),
        load_default=list,
        dump_default=list,
    )
    instance_filter = mm_fields.List(
        mm_fields.Str(),
        load_default=list,
        dump_default=list,
    )
    # noinspection PyTypeChecker
    sort = mm_fields.Str(
        allow_none=True,
        load_default=None,
        dump_default=None,
        validate=AdapterFetchHistorySchema.validate_attr,
    )
    exclude_realtime = SchemaBool(load_default=False, dump_default=False)
    time_range = mm_fields.Nested(TimeRangeSchema(), load_default=TimeRange, dump_default=TimeRange)
    page = mm_fields.Nested(
        PaginationSchema(), load_default=PaginationRequest, dump_default=PaginationRequest
    )
    search = mm_fields.Str(allow_none=True, load_default="", dump_default="")
    filter = mm_fields.Str(allow_none=True, load_default="", dump_default="")

    class Meta:
        """JSONAPI config."""

        type_ = "history_request_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return AdapterFetchHistoryRequest

    # noinspection PyUnusedLocal
    @marshmallow.post_dump
    def post_dump_process(self, data, **kwargs) -> dict:
        """Pass."""
        if "sort" in data and data["sort"] is None:
            data.pop("sort")
        return data

    @classmethod
    def validate_attrs(cls) -> dict:
        """Pass."""
        return AdapterFetchHistorySchema.validate_attrs()


SCHEMA = AdapterFetchHistoryRequestSchema()


@dataclasses.dataclass
class AdapterFetchHistoryRequest(BaseModel):
    """Model for requesting fetch history."""

    adapters_filter: t.List[str] = field_from_mm(SCHEMA, "adapters_filter")
    clients_filter: t.List[str] = field_from_mm(SCHEMA, "clients_filter")
    connection_labels_filter: t.List[str] = field_from_mm(SCHEMA, "connection_labels_filter")
    instance_filter: t.List[str] = field_from_mm(SCHEMA, "instance_filter")
    statuses_filter: t.List[str] = field_from_mm(SCHEMA, "statuses_filter")
    exclude_realtime: bool = field_from_mm(SCHEMA, "exclude_realtime")
    page: t.Optional[PaginationRequest] = field_from_mm(SCHEMA, "page")
    time_range: t.Optional[TimeRange] = field_from_mm(SCHEMA, "time_range")
    sort: t.Optional[str] = field_from_mm(SCHEMA, "sort")
    search: str = field_from_mm(SCHEMA, "search")
    filter: t.Optional[str] = field_from_mm(SCHEMA, "filter")

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    def __post_init__(self):
        """Pass."""
        if self.page is None:
            self.page = PaginationRequest()

        if self.time_range is None:
            self.time_range = TimeRange()

    def set_sort(self, value: t.Optional[str] = None, descending: bool = False) -> t.Optional[str]:
        """Pass."""
        if isinstance(value, str) and value:
            value = AdapterFetchHistorySchema.validate_attr(value=value, exc_cls=NotFoundError)
            value = self._prepend_sort(value=value, descending=descending)
        else:
            value = None

        self.sort = value
        return value

    # noinspection PyShadowingBuiltins
    def set_search_filter(
        self, search: t.Optional[str] = None, filter: t.Optional[str] = None
    ) -> t.Tuple[t.Optional[str], t.Optional[str]]:
        """Pass."""
        values = [search, filter]
        is_strs = [isinstance(x, str) and x for x in values]
        if any(is_strs) and not all(is_strs):
            raise ApiError(f"Only search or filter supplied, must supply both: {values}")
        if not all(is_strs):
            search = ""
            filter = None
        self.search = search
        self.filter = filter
        return search, filter

    def set_filters(
        self,
        history_filters: "AdapterFetchHistoryFilters",
        value_type: str,
        value: t.Optional[t.List[str]] = None,
    ) -> t.List[str]:
        """Pass."""
        value = history_filters.check_value(value_type=value_type, value=value)
        setattr(self, f"{value_type}_filter", value)
        return value

    def set_exclude_realtime(self, value: bool) -> bool:
        """Pass."""
        value = coerce_bool(value)
        self.exclude_realtime = value
        return value

    def set_time_range(
        self,
        relative_unit_type: UnitTypes = UnitTypes.get_default(),
        relative_unit_count: t.Optional[int] = None,
        absolute_date_start: t.Optional[datetime.datetime] = None,
        absolute_date_end: t.Optional[datetime.datetime] = None,
    ) -> "TimeRange":
        """Pass."""
        value = TimeRange.build(
            relative_unit_type=relative_unit_type,
            relative_unit_count=relative_unit_count,
            absolute_date_start=absolute_date_start,
            absolute_date_end=absolute_date_end,
        )
        self.time_range = value
        return value

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return AdapterFetchHistoryRequestSchema
