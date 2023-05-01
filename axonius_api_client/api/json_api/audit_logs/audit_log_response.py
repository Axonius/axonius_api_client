# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import re
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ....exceptions import ApiError
from ....tools import coerce_int_float, dt_now, dt_parse, listify, trim_float
from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaDatetime, field_from_mm


class AuditLogSchema(BaseSchemaJson):
    """Schema for response to get audit logs."""

    action = mm_fields.Str()
    category = mm_fields.Str()
    date = SchemaDatetime()
    message = mm_fields.Str()
    type = mm_fields.Str()
    user = mm_fields.Str()
    role = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    impersonator_user = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    data_scope = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    discovery_cycle_id = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)

    class Meta:
        """JSONAPI config."""

        type_ = "audit_schema"

    @classmethod
    def get_model_cls(cls) -> t.Any:
        """Get the model for this schema."""
        return AuditLog


SCHEMA = AuditLogSchema()


@dataclasses.dataclass
class AuditLog(BaseModel):
    """Response to get audit logs."""

    action: str = field_from_mm(SCHEMA, "action")
    category: str = field_from_mm(SCHEMA, "category")
    date: datetime.datetime = field_from_mm(SCHEMA, "date")
    message: str = field_from_mm(SCHEMA, "message")
    type: str = field_from_mm(SCHEMA, "type")
    user: str = field_from_mm(SCHEMA, "user")
    role: t.Optional[str] = field_from_mm(SCHEMA, "role")
    impersonator_user: t.Optional[str] = field_from_mm(SCHEMA, "impersonator_user")
    data_scope: t.Optional[str] = field_from_mm(SCHEMA, "data_scope")
    discovery_cycle_id: t.Optional[str] = field_from_mm(SCHEMA, "discovery_cycle_id")

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[AuditLogSchema] = SCHEMA

    @classmethod
    def get_schema_cls(cls) -> t.Any:
        """Get the schema for this model."""
        return AuditLogSchema

    @staticmethod
    def _search_properties() -> t.List[str]:
        return [
            "action",
            "category",
            "type",
            "message",
            "user",
        ]

    @staticmethod
    def _str_properties() -> t.List[str]:
        """Pass."""
        return [
            "action",
            "category",
            "date",
            "hours_ago",
            "discovery_cycle_id",
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
    def hours_ago(self) -> float:
        """Pass."""
        return trim_float(value=(dt_now() - self.date).total_seconds() / 60 / 60)

    def within_last_hours(self, hours: t.Optional[t.Union[int, float]] = None) -> bool:
        """Pass."""
        return coerce_int_float(value=hours) >= self.hours_ago if hours else True

    def within_dates(
        self,
        start: t.Optional[t.Union[str, datetime.datetime]] = None,
        end: t.Optional[t.Union[str, datetime.datetime]] = None,
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
                hits.append({"property": prop, "token": value})

        return True if (hits or not all_searches) else False
