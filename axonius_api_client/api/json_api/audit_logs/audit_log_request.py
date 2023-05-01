# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

from ..custom_fields import SchemaDatetime, field_from_mm
from ..resources import ResourcesGet, ResourcesGetSchema


class AuditLogRequestSchema(ResourcesGetSchema):
    """Schema for request to get audit logs."""

    date_from = SchemaDatetime(allow_none=True, load_default=None, dump_default=None)
    date_to = SchemaDatetime(allow_none=True, load_default=None, dump_default=None)

    class Meta:
        """JSONAPI config."""

        type_ = "audit_request_schema"

    @classmethod
    def get_model_cls(cls) -> t.Any:
        """Get the model for this schema."""
        return AuditLogRequest


SCHEMA = AuditLogRequestSchema()


@dataclasses.dataclass
class AuditLogRequest(ResourcesGet):
    """Request to get audit logs."""

    date_from: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "date_from")
    date_to: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "date_to")

    @classmethod
    def get_schema_cls(cls) -> t.Any:
        """Get the schema for this model."""
        return AuditLogRequestSchema
