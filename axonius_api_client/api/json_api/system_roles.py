# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import Optional, Type

import marshmallow
import marshmallow_jsonapi

from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm


class SystemRoleSchema(BaseSchemaJson):
    """Pass."""

    uuid = marshmallow_jsonapi.fields.Str(required=True)
    name = marshmallow_jsonapi.fields.Str(required=True)
    permissions = marshmallow_jsonapi.fields.Dict()
    predefined = SchemaBool(default=False)
    last_updated = SchemaDatetime(allow_none=True)
    asset_scope_restriction = marshmallow_jsonapi.fields.Dict(required=False)
    # PBUG: not modeled well

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SystemRole

    class Meta:
        """Pass."""

        type_ = "roles_details_schema"
        # PBUG: why is this called roles_details_schema vs roles_schema?


class SystemRoleUpdateSchema(SystemRoleSchema):
    """Pass."""

    last_updated = SchemaDatetime(allow_none=True)

    @marshmallow.post_load
    def post_load_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        asr = data.get("asset_scope_restriction", {}) or {}
        if not asr:
            data["asset_scope_restriction"] = {"enabled": False}
        return data

    @marshmallow.post_dump
    def post_dump_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        data.pop("last_updated", None)
        data.pop("id", None)
        data.pop("uuid", None)
        data.pop("predefined", None)
        # PBUG: these should really just be ignored by rest api

        asr = data.get("asset_scope_restriction", {}) or {}
        if not asr:
            data["asset_scope_restriction"] = asr = {"enabled": False}
        asr.pop("asset_scope", None)
        # PBUG: ASR seems to be quite poorly modeled
        return data

    class Meta:
        """Pass."""

        type_ = "roles_schema"
        # PBUG: why is this called roles_details_schema vs roles_schema?


@dataclasses.dataclass
class SystemRole(BaseModel):
    """Pass."""

    name: str
    uuid: str

    asset_scope_restriction: Optional[dict] = dataclasses.field(default_factory=dict)
    predefined: bool = False
    permissions: dict = dataclasses.field(default_factory=dict)
    last_updated: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    id: Optional[str] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SystemRoleSchema

    def __post_init__(self):
        """Pass."""
        if self.id is None and self.uuid is not None:
            self.id = self.uuid
        if not self.asset_scope_restriction:
            self.asset_scope_restriction = {"enabled": False}
        # PBUG: ASR seems to be quite poorly modeled

    def to_dict_old(self):
        """Pass."""
        obj = self.to_dict()
        obj["permissions_flat"] = self.permissions_flat()
        return obj

    def permissions_flat(self) -> dict:
        """Parse a roles permissions into a flat structure."""
        parsed = {}
        for cat, actions in self.permissions.items():
            parsed[cat] = {}
            for action, value in actions.items():
                if isinstance(value, dict):
                    for sub_cat, sub_value in value.items():
                        parsed[cat][f"{action}.{sub_cat}"] = sub_value
                    continue

                parsed[cat][action] = value
        return parsed


class SystemRoleCreateSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    permissions = marshmallow_jsonapi.fields.Dict(required=True)
    asset_scope_restriction = marshmallow_jsonapi.fields.Dict(required=False)

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SystemRoleCreate

    class Meta:
        """Pass."""

        type_ = "roles_schema"

    @marshmallow.post_load
    def post_load_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        asr = data.get("asset_scope_restriction", {}) or {}
        if not asr:
            data["asset_scope_restriction"] = {"enabled": False}
        # PBUG: ASR seems to be quite poorly modeled
        return data

    @marshmallow.post_dump
    def post_dump_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        asr = data.get("asset_scope_restriction", {}) or {}
        if not asr:
            data["asset_scope_restriction"] = asr = {"enabled": False}
        asr.pop("asset_scope", None)
        # PBUG: ASR seems to be quite poorly modeled
        return data


@dataclasses.dataclass
class SystemRoleCreate(BaseModel):
    """Pass."""

    name: str
    permissions: dict
    asset_scope_restriction: Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SystemRoleCreateSchema

    def __post_init__(self):
        """Pass."""
        if not self.asset_scope_restriction:
            self.asset_scope_restriction = {"enabled": False}
        # PBUG: ASR seems to be quite poorly modeled
