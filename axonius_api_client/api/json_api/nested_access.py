# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow
import marshmallow_jsonapi

from ...data import BaseEnum
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import get_field_dc_mm


class AccessMode(BaseEnum):
    """Pass."""

    public: str = "Public"
    private: str = "Private"
    restricted: str = "Restricted"
    shared: str = "Shared"

    @classmethod
    def get_default(cls) -> str:
        """Pass."""
        return cls.public.value

    @classmethod
    def key_mode(self) -> str:
        """Pass."""
        return "mode"

    @classmethod
    def get_access_bool(cls, value: bool) -> dict:
        """Pass."""
        if value:
            return {cls.key_mode(): cls.private.value}
        else:
            return {cls.key_mode(): cls.public.value}


class AccessSchema(BaseSchema):
    """Pass."""

    mode = marshmallow_jsonapi.fields.Str(
        load_default=AccessMode.get_default(),
        dump_default=AccessMode.get_default(),
        description="The level of access restricting the module",
        validate=marshmallow.validate.OneOf(AccessMode.values()),
    )
    config = marshmallow_jsonapi.fields.Dict(
        load_default={},
        dump_default={},
        description="Extra configuration details for the level of access",
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return Access

    class Meta:
        """Pass."""

        type_ = "access_schema"  # Required


class AccessSchemaJson(BaseSchemaJson):
    """Pass."""

    mode = marshmallow_jsonapi.fields.Str(
        load_default=AccessMode.get_default(),
        dump_default=AccessMode.get_default(),
        description="The level of access restricting the module",
        validate=marshmallow.validate.OneOf(AccessMode.values()),
    )
    config = marshmallow_jsonapi.fields.Dict(
        load_default={},
        dump_default={},
        description="Extra configuration details for the level of access",
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return Access

    class Meta:
        """Pass."""

        type_ = "access_schema"  # Required


@dataclasses.dataclass
class Access(BaseModel):
    """Pass."""

    mode: str = get_field_dc_mm(
        mm_field=AccessSchema._declared_fields["mode"], default=AccessMode.get_default()
    )
    config: t.Optional[dict] = get_field_dc_mm(
        mm_field=AccessSchema._declared_fields["config"], default_factory=dict
    )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return AccessSchema
