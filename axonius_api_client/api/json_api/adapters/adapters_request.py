# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, field_from_mm


class AdaptersRequestSchema(BaseSchemaJson):
    """Schema for requesting adapters."""

    filter = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    get_clients = SchemaBool(load_default=False, dump_default=False)

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return AdaptersRequest

    class Meta:
        """JSONAPI config."""

        type_ = "adapters_request_schema"


SCHEMA = AdaptersRequestSchema()


@dataclasses.dataclass
class AdaptersRequest(BaseModel):
    """Model for requesting adapters."""

    filter: t.Optional[str] = field_from_mm(SCHEMA, "filter")
    # PBUG: how is this even used?
    get_clients: bool = field_from_mm(SCHEMA, "get_clients")

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return AdaptersRequestSchema
