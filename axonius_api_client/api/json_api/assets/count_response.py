# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import field_from_mm


class CountSchema(BaseSchemaJson):
    """Pass."""

    value = mm_fields.Int(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Count of assets matching the supplied filter",
    )

    class Meta:
        """Pass."""

        type_ = "int_value_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model class."""
        return Count


SCHEMA = CountSchema()


@dataclasses.dataclass
class Count(BaseModel):
    """Pass."""

    value: t.Optional[int] = field_from_mm(SCHEMA, "value")
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CountSchema
