# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import field_from_mm


class AdapterSettingsUpdateUpdateSchema(BaseSchemaJson):
    """Schema for updating adapter settings."""

    config = mm_fields.Dict(required=True)
    configName = mm_fields.Str(load_default="", dump_default="")
    pluginId = mm_fields.Str(load_default="", dump_default="")
    prefix = mm_fields.Str(load_default="adapters", dump_default="adapters")

    class Meta:
        """JSONAPI config."""

        type_ = "settings_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return AdapterSettingsUpdate


SCHEMA = AdapterSettingsUpdateUpdateSchema()


@dataclasses.dataclass
class AdapterSettingsUpdate(BaseModel):
    """Model for updating adapter settings."""

    config: dict = field_from_mm(SCHEMA, "config")
    pluginId: str = field_from_mm(SCHEMA, "pluginId")
    configName: str = field_from_mm(SCHEMA, "configName")
    prefix: str = field_from_mm(SCHEMA, "prefix")

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return AdapterSettingsUpdateUpdateSchema
