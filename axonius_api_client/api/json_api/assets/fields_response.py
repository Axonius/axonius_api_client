# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ..generic import Metadata, MetadataSchema


class FieldsSchema(MetadataSchema):
    """Schema for response from getting field schemas for an asset type."""

    class Meta:
        """JSONAPI type."""

        type_ = "metadata_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return Fields


SCHEMA = FieldsSchema()


@dataclasses.dataclass
class Fields(Metadata):
    """Model for response from getting field schemas for an asset type."""

    SCHEMA: t.ClassVar[t.Any] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return FieldsSchema
