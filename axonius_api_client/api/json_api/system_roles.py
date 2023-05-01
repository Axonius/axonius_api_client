# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import math
import typing as t

import marshmallow
import marshmallow_jsonapi
from cachetools import TTLCache, cached

from .base import BaseModel, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm
from .data_scopes import DataScope


def parse_cat_actions(raw: dict) -> dict:
    """Parse the permission labels into a layered dict."""

    def set_len(item, target):
        measure = int(math.ceil(len(item) / 10.0)) * 10
        if measure > lengths[target]:
            lengths[target] = measure

    cats = {}
    cat_actions = {}
    lengths = {"categories": 0, "actions": 0, "categories_desc": 0, "actions_desc": 0}

    # first pass, get all the categories
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

    # second pass, get all the actions
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

    return data


def build_data_scope_restriction(
    obj: t.Any = None,
    enabled: bool = False,
    data_scope: t.Optional[str] = None,
) -> dict:
    """Pass."""
    if not isinstance(obj, dict):
        obj = {}

    enabled = obj.get("enabled", enabled)
    data_scope = obj.get("data_scope", data_scope)

    ret = {}
    ret["enabled"] = enabled
    ret["data_scope"] = data_scope
    return ret


def fix_data_scope_restriction(data: dict) -> dict:
    """Pass."""
    # PBUG: ASR seems to be quite poorly modeled
    data["data_scope_restriction"] = build_data_scope_restriction(
        data.get("data_scope_restriction")
    )
    return data


class SystemRoleSchema(BaseSchemaJson):
    """Pass."""

    uuid = marshmallow_jsonapi.fields.Str(required=True)
    name = marshmallow_jsonapi.fields.Str(required=True)
    permissions = marshmallow_jsonapi.fields.Dict(required=True)
    data_scope_restriction = marshmallow_jsonapi.fields.Dict(required=False)

    predefined = SchemaBool(load_default=False, dump_default=False)
    last_updated = SchemaDatetime(allow_none=True)
    # NEW_IN: 05/31/21 cortex/develop
    users_count = marshmallow_jsonapi.fields.Int(required=False, load_default=0, dump_default=0)

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return SystemRole

    class Meta:
        """Pass."""

        type_ = "roles_details_schema"
        # PBUG: why is this called roles_details_schema vs roles_schema?


class SystemRoleUpdateSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    permissions = marshmallow_jsonapi.fields.Dict(required=True)
    data_scope_restriction = marshmallow_jsonapi.fields.Dict(required=False)

    @marshmallow.post_load
    def post_load_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        return fix_data_scope_restriction(data)

    @marshmallow.post_dump
    def post_dump_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        data = fix_data_scope_restriction(data)
        return data

    class Meta:
        """Pass."""

        type_ = "roles_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return SystemRoleUpdate


class SystemRoleCreateSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    permissions = marshmallow_jsonapi.fields.Dict(required=True)
    data_scope_restriction = marshmallow_jsonapi.fields.Dict(required=False)

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return SystemRoleCreate

    class Meta:
        """Pass."""

        type_ = "roles_schema"

    @marshmallow.post_load
    def post_load_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        return fix_data_scope_restriction(data)

    @marshmallow.post_dump
    def post_dump_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        return fix_data_scope_restriction(data)


@dataclasses.dataclass
class SystemRole(BaseModel):
    """Pass."""

    uuid: str
    name: str
    permissions: dict
    data_scope_restriction: t.Optional[dict] = dataclasses.field(default_factory=dict)

    predefined: bool = False
    last_updated: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    id: t.Optional[str] = None

    # NEW_IN: 05/31/21 cortex/develop
    users_count: int = 0
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @marshmallow.post_load
    def post_load_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        return fix_data_scope_restriction(data)

    @marshmallow.post_dump
    def post_dump_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        return fix_data_scope_restriction(data)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SystemRoleSchema

    def __post_init__(self):
        """Pass."""
        self.id = self.uuid if self.id is None and self.uuid is not None else self.id
        self.data_scope_restriction = build_data_scope_restriction(self.data_scope_restriction)

    def to_dict_old(self) -> dict:
        """Pass."""
        obj = self.to_dict()
        obj["permissions_flat"] = self.permissions_flat()
        obj["permissions_flat_descriptions"] = self.permissions_flat_descriptions()
        obj["data_scope_name"] = self.data_scope_name
        return obj

    @property
    def data_scope_name(self) -> t.Optional[str]:
        """Pass."""
        if isinstance(self.data_scope, DataScope):
            return self.data_scope.name
        return None

    @property
    def data_scope(self) -> t.Optional[DataScope]:
        """Pass."""
        if not hasattr(self, "_data_scope"):
            self._data_scope = None
            if isinstance(self.data_scope_id, str) and self.data_scope_id.strip():
                self._data_scope = self.HTTP.CLIENT.data_scopes.get_cached_single(
                    value=self.data_scope_id
                )
        return self._data_scope

    @property
    def data_scope_id(self) -> t.Optional[str]:
        """Pass."""
        return self.data_scope_restriction.get("data_scope")

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

    def permissions_flat_descriptions(self) -> t.List[dict]:
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


@dataclasses.dataclass
class SystemRoleUpdate(BaseModel):
    """Pass."""

    name: str
    permissions: dict
    data_scope_restriction: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SystemRoleUpdateSchema


@dataclasses.dataclass
class SystemRoleCreate(BaseModel):
    """Pass."""

    name: str
    permissions: dict
    data_scope_restriction: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SystemRoleCreateSchema

    def __post_init__(self):
        """Pass."""
        self.data_scope_restriction = build_data_scope_restriction(self.data_scope_restriction)
