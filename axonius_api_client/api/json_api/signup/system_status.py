# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, field_from_mm


class SystemStatusSchema(BaseSchemaJson):
    """Schema for system status response."""

    msg = mm_fields.Str()
    is_ready = SchemaBool()
    status_code = mm_fields.Int()

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return SystemStatus

    class Meta:
        """JSONAPI config."""

        type_ = "machine_status_schema"


SCHEMA: BaseSchemaJson = SystemStatusSchema()


@dataclasses.dataclass
class SystemStatus(BaseModel):
    """Model for system status response."""

    msg: str = field_from_mm(SCHEMA, "msg")
    is_ready: bool = field_from_mm(SCHEMA, "is_ready")
    status_code: int = field_from_mm(SCHEMA, "status_code")
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return SystemStatusSchema

    def __str__(self) -> str:
        """Human string."""
        msg = self.msg or "none"
        return f"System status - ready: {self.is_ready}, message: {msg} (code: {self.status_code})"
