# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import math
from typing import List, Optional, Type

import marshmallow
import marshmallow_jsonapi
from cachetools import TTLCache, cached

from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm


def parse_cat_actions(raw: dict) -> dict:
    """Parse the permission labels into a layered dict."""

    def set_len(item, target):
        measure = int(math.ceil(len(item) / 10.0)) * 10
        if measure > lengths[target]:
            lengths[target] = measure

    cats = {}
    cat_actions = {}
    lengths = {"categories": 0, "actions": 0, "categories_desc": 0, "actions_desc": 0}

    # first pass, get all of the categories
    for label, desc in raw.items():
        pre, rest = label.split(".", 1)
        if pre != "permissions":
            continue

        split = rest.split(".", 1)
        cat = split.pop(0)

        if not split:
            assert cat not in cats
            assert cat not in cat_actions
            cats[cat] = desc
            set_len(item=desc, target="categories_desc")
            set_len(item=cat, target="categories")

            cat_actions[cat] = {}

    # second pass, get all of the actions
    for label, desc in raw.items():
        pre, rest = label.split(".", 1)
        if pre != "permissions":
            continue

        split = rest.split(".", 1)
        cat = split.pop(0)

        if not split:
            continue

        action = split.pop(0)
        assert not split
        assert action not in cat_actions[cat]
        set_len(item=desc, target="actions_desc")
        set_len(item=action, target="actions")
        cat_actions[cat][action] = desc

    return {"categories": cats, "actions": cat_actions, "lengths": lengths}


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def cat_actions(http) -> dict:
    """Get permission categories and their actions."""
    from .. import ApiEndpoints

    api_endpoint = ApiEndpoints.system_roles.perms
    labels = api_endpoint.perform_request(http=http)
    data = parse_cat_actions(raw=labels)

    # flags = feature_flags(http=http)

    # if not flags.has_cloud_compliance:  # pragma: no cover
    #     data["categories"].pop("compliance")
    #     data["actions"].pop("compliance")
    return data


def feature_flags(http):
    """Direct API method to get the feature flags for the core."""
    from .. import ApiEndpoints

    api_endpoint = ApiEndpoints.system_settings.feature_flags_get
    return api_endpoint.perform_request(http=http)


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
        return cat_actions(http=self.HTTP)

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
