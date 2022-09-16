# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import List, Optional, Type

import marshmallow_jsonapi

from .base import BaseModel, BaseSchema
from .custom_fields import SchemaBool, get_schema_dc


class IdSelectionSchema(BaseSchema):
    """Pass."""

    ids = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str(), required=True)
    include = SchemaBool(load_default=True, dump_default=True)

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return IdSelection


@dataclasses.dataclass
class IdSelection(BaseModel):
    """Pass."""

    ids: List[str] = get_schema_dc(schema=IdSelectionSchema, key="ids")
    include: bool = get_schema_dc(schema=IdSelectionSchema, key="include", default=True)

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return IdSelectionSchema
