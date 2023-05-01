# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ..generic import IntValue, IntValueSchema


class ModifyTagsSchema(IntValueSchema):
    """Schema for response from modifying tags."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return ModifyTags

    class Meta:
        """JSONAPI config."""

        type_ = "int_value_schema"


@dataclasses.dataclass
class ModifyTags(IntValue):
    """Model for response from modifying tags."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return ModifyTagsSchema
