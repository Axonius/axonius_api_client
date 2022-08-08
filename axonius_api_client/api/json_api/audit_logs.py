# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import re
from typing import List, Optional, Type, Union

import marshmallow_jsonapi

from ...exceptions import ApiError
from ...tools import coerce_int_float, dt_now, dt_parse, listify, trim_float
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaDatetime, get_field_dc_mm
from .resources import ResourcesGet, ResourcesGetSchema


class AuditLogRequestSchema(ResourcesGetSchema):
    """Pass."""

    date_from = SchemaDatetime(allow_none=True)
    date_to = SchemaDatetime(allow_none=True)

    class Meta:
        """Pass."""

        type_ = "audit_request_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return AuditLogRequest


@dataclasses.dataclass
class AuditLogRequest(ResourcesGet):
    """Pass."""

    date_from: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    date_to: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return AuditLogRequestSchema


class AuditLogSchema(BaseSchemaJson):
    """Pass."""

    action = marshmallow_jsonapi.fields.Str()
    category = marshmallow_jsonapi.fields.Str()
    date = SchemaDatetime()
    message = marshmallow_jsonapi.fields.Str()
    type = marshmallow_jsonapi.fields.Str()
    user = marshmallow_jsonapi.fields.Str()
    role = marshmallow_jsonapi.fields.Str(allow_none=True)
    impersonator_user = marshmallow_jsonapi.fields.Str(allow_none=True)
    data_scope = marshmallow_jsonapi.fields.Str(allow_none=True)

    class Meta:
        """Pass."""

        type_ = "audit_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return AuditLog


@dataclasses.dataclass
class AuditLog(BaseModel):
    """Pass."""

    action: str
    category: str
    date: datetime.datetime = get_field_dc_mm(mm_field=SchemaDatetime())
    message: str
    type: str
    user: str
    role: Optional[str] = None
    impersonator_user: Optional[str] = None
    data_scope: Optional[str] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return AuditLogSchema

    @staticmethod
    def _search_properties() -> List[str]:
        return [
            "action",
            "category",
            "type",
            "message",
            "user",
        ]

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "action",
            "category",
            "date",
            "hours_ago",
            "message",
            "type",
            "user",
            "role",
            "impersonator_user",
            "data_scope",
        ]

    @staticmethod
    def _str_join() -> str:
        """Pass."""
        return ", "

    @property
    def hours_ago(self) -> str:
        """Pass."""
        return trim_float(value=(dt_now() - self.date).total_seconds() / 60 / 60)

    def within_last_hours(self, hours: Optional[Union[int, float]] = None) -> bool:
        """Pass."""
        return coerce_int_float(value=hours) >= self.hours_ago if hours else True

    def within_dates(
        self,
        start: Optional[Union[str, datetime.datetime]] = None,
        end: Optional[Union[str, datetime.datetime]] = None,
    ) -> bool:
        """Pass."""
        start_match = True
        end_match = True

        if start:
            start = dt_parse(obj=start, default_tz_utc=True)
            start_match = self.date >= start

        if end:
            end = dt_parse(obj=end, default_tz_utc=True)
            end_match = end >= self.date

        return start_match and end_match

    def property_searches(self, **kwargs) -> bool:
        """Pass."""
        valid = self._search_properties()

        invalids = [x for x in kwargs if x not in valid]
        if invalids:
            raise ApiError(f"Invalid properties {invalids!r}, must be one of {', '.join(valid)}")

        all_searches = []
        hits = []
        for prop, searches in kwargs.items():
            searches = listify(searches)
            all_searches += searches
            value = getattr(self, prop) or ""
            if any([re.search(x, value, re.I) for x in searches]):
                hits.append({"propery": prop, "value": value})

        return True if (hits or not all_searches) else False
