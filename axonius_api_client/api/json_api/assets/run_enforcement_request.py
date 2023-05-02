# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import field_from_mm
from ..selection import IdSelection, IdSelectionSchema


class RunEnforcementRequestSchema(BaseSchemaJson):
    """Schema for request to run an enforcement."""

    name = mm_fields.Str(
        required=True,
        description="Name of the enforcement to run",
    )
    selection = mm_fields.Nested(
        IdSelectionSchema(),
        required=True,
        description="Selection of assets to run the enforcement against",
    )
    filter = mm_fields.Str(
        load_default="",
        dump_default="",
        description="Filter of assets to run the enforcement against?",
    )
    view = mm_fields.Dict(
        load_default=dict,
        dump_default=dict,
        description="View of assets to run the enforcement against? seems unused",
    )

    class Meta:
        """JSONAPI config."""

        type_ = "enforce_entity_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return RunEnforcementRequest


SCHEMA = RunEnforcementRequestSchema()


@dataclasses.dataclass
class RunEnforcementRequest(BaseModel):
    """Pass."""

    name: str = field_from_mm(SCHEMA, "name")
    selection: IdSelection = field_from_mm(SCHEMA, "selection")
    filter: str = field_from_mm(SCHEMA, "filter")
    view: dict = field_from_mm(SCHEMA, "view")

    SCHEMA: t.ClassVar[t.Any] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return RunEnforcementRequestSchema
