# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, field_from_mm


class CnxCreateSchema(BaseSchemaJson):
    """Schema for response from creating a connection."""

    active = SchemaBool()
    client_id = mm_fields.Str()
    status = mm_fields.Str()
    error = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    failed_connections_limit_exceeded = mm_fields.Int(
        allow_none=True, load_default=None, dump_default=None
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return CnxCreate

    class Meta:
        """JSONAPI config."""

        type_ = "connections_details_schema"


SCHEMA = CnxCreateSchema()


@dataclasses.dataclass
class CnxCreate(BaseModel):
    """Model for response from creating a connection."""

    status: str = field_from_mm(SCHEMA, "status")
    client_id: str = field_from_mm(SCHEMA, "client_id")
    id: str = field_from_mm(SCHEMA, "id")
    active: bool = field_from_mm(SCHEMA, "active")
    error: t.Optional[str] = field_from_mm(SCHEMA, "error")
    failed_connections_limit_exceeded: t.Optional[int] = field_from_mm(
        SCHEMA, "failed_connections_limit_exceeded"
    )

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return CnxCreateSchema

    @property
    def uuid(self) -> str:
        """Pass."""
        return self.id

    @staticmethod
    def _str_properties() -> t.List[str]:
        """Pass."""
        return ["client_id", "uuid", "status", "error"]

    @property
    def working(self) -> bool:
        """Pass."""
        return self.status == "success" and not self.error
