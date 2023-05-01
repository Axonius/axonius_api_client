# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, SchemaDatetime, field_from_mm


class AssetByIdRequestSchema(BaseSchemaJson):
    """Marshmallow schema for getting a single asset by internal_axon_id."""

    history = SchemaDatetime(
        load_default=None,
        dump_default=None,
        allow_none=True,
        documentation="Get asset as it was at this time",
    )
    return_empty_details = SchemaBool(
        load_default=True,
        dump_default=True,
        documentation="Unknown",
    )

    class Meta:
        """JSONAPI type for HistoryDatesSchema."""

        type_ = "history_dates_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return AssetByIdRequest


SCHEMA = AssetByIdRequestSchema()


@dataclasses.dataclass
class AssetByIdRequest(BaseModel):
    """Model for getting a single asset by internal_axon_id."""

    history: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "history")
    return_empty_details: bool = field_from_mm(SCHEMA, "return_empty_details")

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return AssetByIdRequestSchema
