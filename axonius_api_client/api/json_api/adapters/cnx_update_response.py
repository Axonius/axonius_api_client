# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ..base import BaseSchemaJson
from .cnx_create_response import CnxCreate, CnxCreateSchema


class CnxUpdateSchema(CnxCreateSchema):
    """Schema for response from updating a connection."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return CnxUpdate

    class Meta:
        """JSONAPI config."""

        type_ = "connections_details_schema"


SCHEMA = CnxUpdateSchema()


@dataclasses.dataclass
class CnxUpdate(CnxCreate):
    """Model for response from updating a connection."""

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return CnxUpdateSchema
