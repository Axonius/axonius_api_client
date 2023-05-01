# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import field_from_mm


class CnxTestRequestSchema(BaseSchemaJson):
    """Schema for request to test a connection."""

    connection = mm_fields.Dict(
        required=True,
        description="Connection settings",
    )
    instance = mm_fields.Str(
        required=True,
        description="ID of instance to test connection with",
    )
    tunnel_id = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="ID of tunnel to use for connection",
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return CnxTestRequest

    class Meta:
        """JSONAPI config."""

        type_ = "test_connection_schema"


SCHEMA = CnxTestRequestSchema()


@dataclasses.dataclass
class CnxTestRequest(BaseModel):
    """Model for request to test a connection."""

    connection: dict = field_from_mm(SCHEMA, "connection")
    instance: str = field_from_mm(SCHEMA, "instance")
    tunnel_id: t.Optional[str] = field_from_mm(SCHEMA, "tunnel_id")

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return CnxTestRequestSchema
