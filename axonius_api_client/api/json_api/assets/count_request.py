# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields

from ....tools import dt_now, dt_parse, get_query_id
from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, SchemaDatetime, field_from_mm


class CountRequestSchema(BaseSchemaJson):
    """Pass."""

    history = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Get the count of assets matching filter for a specific date",
    )  # FilterSchema
    search = mm_fields.Str(
        load_default="",
        dump_default="",
        allow_none=True,
        description="unknown",
    )  #
    # FilterSchema
    filter = mm_fields.Str(
        load_default="",
        dump_default="",
        allow_none=True,
        description="AQL to filter assets",
    )  #
    # FilterSchema
    use_heavy_fields_collection = SchemaBool(
        load_default=False,
        dump_default=False,
        description="unknown",
    )  # ForceHeavyFieldsSchema
    use_cache_entry = SchemaBool(
        load_default=False,
        dump_default=False,
        description="Use any previously cached results for this query",
    )  #
    # EntitiesCountSchema
    query_id = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Identifier for this query",
    )  # EntitiesCountSchema
    saved_query_id = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="ID of SQ that triggered this request",
    )  # EntitiesCountSchema
    frontend_sent_time = SchemaDatetime(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Time that the frontend sent this request",
    )  # EntitiesCountSchema

    class Meta:
        """JSONAPI config."""

        type_ = "entities_count_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return CountRequest


SCHEMA = CountRequestSchema()


@dataclasses.dataclass
class CountRequest(BaseModel):
    """Pass."""

    history: t.Optional[str] = field_from_mm(SCHEMA, "history")
    search: t.Optional[str] = field_from_mm(SCHEMA, "search")
    filter: t.Optional[str] = field_from_mm(SCHEMA, "filter")
    use_heavy_fields_collection: bool = field_from_mm(SCHEMA, "use_heavy_fields_collection")
    use_cache_entry: bool = field_from_mm(SCHEMA, "use_cache_entry")
    query_id: t.Optional[str] = field_from_mm(SCHEMA, "query_id")
    saved_query_id: t.Optional[str] = field_from_mm(SCHEMA, "saved_query_id")
    frontend_sent_time: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "frontend_sent_time")

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CountRequestSchema

    def __post_init__(self):
        """Pass."""
        self.query_id: str = get_query_id(self.query_id)
        self.frontend_sent_time: t.Optional[datetime.datetime] = dt_parse(
            obj=self.frontend_sent_time, allow_none=True, as_none=dt_now(), default_tz_utc=True
        )
