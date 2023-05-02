# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import field_from_mm


class CnxDeleteSchema(BaseSchemaJson):
    """Schema for response to delete a connection."""

    client_id = mm_fields.Str()

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return CnxDelete

    class Meta:
        """JSONAPI config."""

        type_ = "deleted_connections_schema"


SCHEMA = CnxDeleteSchema()


@dataclasses.dataclass
class CnxDelete(BaseModel):
    """Model for response to delete a connection."""

    client_id: str = field_from_mm(SCHEMA, "client_id")

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    def __post_init__(self):
        """Pass."""
        # noinspection PyBroadException
        try:
            self.client_id = eval(self.client_id)["client_id"]
        except Exception:  # pragma: no cover
            pass

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return CnxDeleteSchema
