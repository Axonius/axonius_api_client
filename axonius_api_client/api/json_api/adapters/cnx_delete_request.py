# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, field_from_mm


class CnxDeleteRequestSchema(BaseSchemaJson):
    """Schema for request to delete a connection."""

    is_instances_mode = SchemaBool(load_default=False, dump_default=False)
    delete_entities = SchemaBool(load_default=False, dump_default=False)
    instance = mm_fields.Str()
    instance_name = mm_fields.Str()

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return CnxDeleteRequest

    class Meta:
        """JSONAPI config."""

        type_ = "delete_connections_schema"


SCHEMA = CnxDeleteRequestSchema()


@dataclasses.dataclass
class CnxDeleteRequest(BaseModel):
    """Model for request to delete a connection."""

    instance: str = field_from_mm(SCHEMA, "instance")
    instance_name: str = field_from_mm(SCHEMA, "instance_name")
    is_instances_mode: bool = field_from_mm(SCHEMA, "is_instances_mode")
    delete_entities: bool = field_from_mm(SCHEMA, "delete_entities")

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return CnxDeleteRequestSchema
