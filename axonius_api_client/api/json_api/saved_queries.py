# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type

import marshmallow_jsonapi

from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm


class SavedQuerySchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    always_cached = SchemaBool(default=False, missing=False)
    asset_scope = marshmallow_jsonapi.fields.Bool(default=False, missing=False)
    private = marshmallow_jsonapi.fields.Bool(default=False, missing=False)
    description = marshmallow_jsonapi.fields.Str(default="", missing="", allow_none=True)
    view = marshmallow_jsonapi.fields.Dict()
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    predefined = marshmallow_jsonapi.fields.Bool(default=False, missing=False)
    date_fetched = marshmallow_jsonapi.fields.Str(allow_none=True, missing=None)
    is_asset_scope_query_ready = SchemaBool()
    is_referenced = SchemaBool()
    query_type = marshmallow_jsonapi.fields.Str()
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    timestamp = marshmallow_jsonapi.fields.Str(allow_none=True)
    last_updated = SchemaDatetime(allow_none=True)
    updated_by = marshmallow_jsonapi.fields.Str(allow_none=True, missing=None)
    user_id = marshmallow_jsonapi.fields.Str(allow_none=True, missing=None)
    uuid = marshmallow_jsonapi.fields.Str(allow_none=True, missing=None)

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SavedQuery

    class Meta:
        """Pass."""

        type_ = "views_details_schema"


@dataclasses.dataclass
class SavedQuery(BaseModel):
    """Pass."""

    id: str
    name: str
    view: dict
    query_type: str
    updated_by: Optional[str] = None
    user_id: Optional[str] = None
    uuid: Optional[str] = None
    date_fetched: Optional[str] = None
    timestamp: Optional[str] = None
    last_updated: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    always_cached: bool = False
    asset_scope: bool = False
    private: bool = False
    description: Optional[str] = ""
    tags: List[str] = dataclasses.field(default_factory=list)
    predefined: bool = False
    is_asset_scope_query_ready: bool = False
    is_referenced: bool = False

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SavedQuerySchema


class SavedQueryCreateSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    view = marshmallow_jsonapi.fields.Dict()
    description = marshmallow_jsonapi.fields.Str(default="", missing="", allow_none=True)
    always_cached = SchemaBool(default=False, missing=False)
    private = marshmallow_jsonapi.fields.Bool(default=False, missing=False)
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SavedQueryCreate

    class Meta:
        """Pass."""

        type_ = "views_schema"


@dataclasses.dataclass
class SavedQueryCreate(BaseModel):
    """Pass."""

    name: str
    view: dict
    description: Optional[str] = ""
    always_cached: bool = False
    private: bool = False
    tags: List[str] = dataclasses.field(default_factory=list)

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SavedQueryCreateSchema
