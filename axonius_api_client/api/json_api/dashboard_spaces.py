# -*- coding: utf-8 -*-
"""Models for API requests & responses."""

import dataclasses
from typing import List, Optional, Type

import marshmallow_jsonapi

from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, get_field_dc_mm


class ExportableSpacesResponseSchema(BaseSchemaJson):
    """Pass."""

    spaces = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(), load_default=[], dump_default=[]
    )

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return ExportableSpacesResponse

    class Meta:
        """Pass."""

        type_ = "export_permitted_spaces_schema"


@dataclasses.dataclass
class ExportableSpacesResponse(BaseModel):
    """Pass."""

    spaces: List[str] = get_field_dc_mm(
        mm_field=ExportableSpacesResponseSchema._declared_fields["spaces"], default_factory=list
    )

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return ExportableSpacesResponseSchema


class ExportSpacesRequestSchema(BaseSchemaJson):
    """Pass."""

    spaces = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(),
        load_default=[],
        dump_default=[],
        description="Spaces names to export",
    )
    as_template = SchemaBool(
        load_default=False, dump_default=False, description="Should this export return a template"
    )

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return ExportSpacesRequest

    class Meta:
        """Pass."""

        type_ = "export_spaces_schema"


@dataclasses.dataclass
class ExportSpacesRequest(BaseModel):
    """Pass."""

    spaces: List[str] = get_field_dc_mm(
        mm_field=ExportSpacesRequestSchema._declared_fields["spaces"], default_factory=list
    )
    as_template: bool = get_field_dc_mm(
        mm_field=ExportSpacesRequestSchema._declared_fields["as_template"], default=False
    )

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return ExportSpacesRequestSchema
