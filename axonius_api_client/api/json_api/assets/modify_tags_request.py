# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import field_from_mm


class ModifyTagsRequestSchema(BaseSchemaJson):
    """Schema for request to modify tags."""

    entities = mm_fields.Dict(
        load_default=dict,
        dump_default=dict,
        description="Entities to modify tags on",
    )
    labels = mm_fields.List(
        mm_fields.Str(),
        load_default=list,
        dump_default=list,
        description="Tags to modify",
    )
    filter = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Filter to use to select assets?",
    )

    class Meta:
        """JSONAPI config."""

        type_ = "add_tags_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return ModifyTagsRequest


SCHEMA = ModifyTagsRequestSchema()


@dataclasses.dataclass
class ModifyTagsRequest(BaseModel):
    """Model for request to modify tags."""

    entities: dict = field_from_mm(SCHEMA, "entities")
    labels: t.List[str] = field_from_mm(SCHEMA, "labels")
    filter: t.Optional[str] = field_from_mm(SCHEMA, "filter")

    SCHEMA: t.ClassVar[t.Any] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return ModifyTagsRequestSchema
