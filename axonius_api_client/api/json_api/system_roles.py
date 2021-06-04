# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type

import marshmallow
import marshmallow_jsonapi

from ..models import DataModel, DataSchema, DataSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm


class SystemRoleSchema(DataSchemaJson):
    """Pass."""

    uuid = marshmallow_jsonapi.fields.Str(required=True)
    name = marshmallow_jsonapi.fields.Str(required=True)
    permissions = marshmallow_jsonapi.fields.Dict()
    predefined = SchemaBool(default=False)
    last_updated = SchemaDatetime(allow_none=True)
    asset_scope_restriction = marshmallow_jsonapi.fields.Dict(required=False)
    # PBUG: not modeled well

    # NEW_IN: 05/31/21 cortex/develop
    users_count = marshmallow_jsonapi.fields.Int(required=False, missing=0)

    @staticmethod
    def _get_model_cls() -> type:
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
    def post_load_fixit(self, data: "SystemRole", **kwargs) -> "SystemRole":
        """Pass."""
        if not data.asset_scope_restriction:
            data.asset_scope_restriction = {"enabled": False}
        # PBUG: ASR seems to be quite poorly modeled
        return data

    @marshmallow.post_dump
    def post_dump_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        data.pop("last_updated", None)
        data.pop("id", None)
        data.pop("uuid", None)
        data.pop("predefined", None)
        # PBUG: these should really just be ignored by rest api

        # NEW_IN: 05/31/21 cortex/develop
        data.pop("users_count", None)

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
class SystemRole(DataModel):
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

    # NEW_IN: 05/31/21 cortex/develop
    users_count: int = 0

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
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
        obj["permissions_flat_descriptions"] = self.permissions_flat_descriptions()
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

    def permissions_desc(self) -> dict:
        """Pass."""
        return self.CLIENT.system_roles.cat_actions()

    def permissions_flat_descriptions(self) -> List[dict]:
        """Pass."""
        ret = []
        permissions = self.permissions_flat()
        descriptions = self.permissions_desc()
        category_descriptions = descriptions["categories"]
        action_descriptions = descriptions["actions"]

        for category_name, actions in action_descriptions.items():
            category_description = category_descriptions.get(category_name)

            for action_name, action_description in actions.items():
                action_value = permissions.get(category_name, {}).get(action_name)
                item = {
                    "Category Name": category_name,
                    "Category Description": category_description,
                    "Action Name": action_name,
                    "Action Description": action_description,
                    "Value": action_value,
                }
                ret.append(item)
        return ret


class SystemRoleCreateSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    permissions = marshmallow_jsonapi.fields.Dict(required=True)
    asset_scope_restriction = marshmallow_jsonapi.fields.Dict(required=False)

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return SystemRoleCreate

    class Meta:
        """Pass."""

        type_ = "roles_schema"

    @marshmallow.post_load
    def post_load_fixit(self, data: "SystemRoleCreate", **kwargs) -> "SystemRoleCreate":
        """Pass."""
        if not data.asset_scope_restriction:
            data.asset_scope_restriction = {"enabled": False}
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
class SystemRoleCreate(DataModel):
    """Pass."""

    name: str
    permissions: dict
    asset_scope_restriction: Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return SystemRoleCreateSchema

    def __post_init__(self):
        """Pass."""
        if not self.asset_scope_restriction:
            self.asset_scope_restriction = {"enabled": False}
        # PBUG: ASR seems to be quite poorly modeled
