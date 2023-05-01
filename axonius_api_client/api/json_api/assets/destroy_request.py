# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow

from ..base import BaseModel, BaseSchema
from ..custom_fields import SchemaBool, field_from_mm


class DestroyRequestSchema(BaseSchema):
    """Schema for request to destroy assets."""

    destroy = SchemaBool(
        load_default=False,
        dump_default=False,
        description="Destroy assets, must be True to destroy assets",
    )
    history = SchemaBool(
        load_default=False,
        dump_default=False,
        description="Destroy assets history, must be True to destroy assets history",
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return DestroyRequest


SCHEMA = DestroyRequestSchema()


@dataclasses.dataclass
class DestroyRequest(BaseModel):
    """Model for request to destroy assets."""

    destroy: bool = field_from_mm(SCHEMA, "destroy")
    history: bool = field_from_mm(SCHEMA, "history")

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return DestroyRequestSchema
