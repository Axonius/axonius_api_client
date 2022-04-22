# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import ClassVar, Dict, List, Optional, Type

import marshmallow
import marshmallow_jsonapi

from ...exceptions import ApiError
from ...tools import json_load
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaDatetime
from .saved_queries import SavedQuery


class UpdatedByMixins:
    """Pass."""

    @property
    def updated_user_obj(self) -> dict:
        """Pass."""
        if not hasattr(self, "_updated_user_obj"):
            self._updated_user_obj = json_load(self.updated_by)
        return self._updated_user_obj

    @property
    def updated_user_name(self) -> str:
        """Get the user name of the user that last updated this object."""
        return self.updated_user_obj.get("user_name") or ""

    @property
    def updated_user_source(self) -> str:
        """Get the source of the user that last updated this object."""
        return self.updated_user_obj.get("source") or ""

    @property
    def updated_user_first_name(self) -> str:
        """Get the first name of the user that last updated this object."""
        return self.updated_user_obj.get("first_name") or ""

    @property
    def updated_user_last_name(self) -> str:
        """Get the last name of the user that last updated this object."""
        return self.updated_user_obj.get("last_name") or ""

    @property
    def updated_user_full_name(self) -> str:
        """Get the first and last name of the user that last updated this object."""
        return " ".join(
            [x for x in [self.updated_user_first_name, self.updated_user_last_name] if x]
        )

    @property
    def updated_user(self) -> str:
        """Pass."""
        return f"{self.updated_user_source}/{self.updated_user_name}"


@dataclasses.dataclass
class DataScope(BaseModel, UpdatedByMixins):
    """Pass."""

    name: str
    uuid: str

    created_at: datetime.datetime = dataclasses.field(
        metadata={"dataclasses_json": {"mm_field": SchemaDatetime()}}
    )
    last_updated: datetime.datetime = dataclasses.field(
        metadata={"dataclasses_json": {"mm_field": SchemaDatetime()}}
    )

    description: str = ""
    updated_by: str = ""

    associated_roles: List[str] = dataclasses.field(default_factory=list)
    users_queries: List[str] = dataclasses.field(default_factory=list)
    devices_queries: List[str] = dataclasses.field(default_factory=list)

    ASSET_SCOPES: ClassVar[Dict[str, List[SavedQuery]]] = None

    def __str__(self) -> str:
        """Pass."""
        users_scopes = [x.name for x in self.users_scopes]
        devices_scopes = [x.name for x in self.devices_scopes]
        items = [
            f"Name: {self.name!r}",
            f"UUID: {self.uuid!r}",
            f"Description: {self.description!r}",
            f"Associated Roles: {self.associated_roles}",
            f"User Asset Scopes: {users_scopes}",
            f"Device Asset Scopes: {devices_scopes}",
            f"Updated Date: {self.last_updated.isoformat()!r}",
            f"Updated User: {self.updated_user!r}",
        ]
        return "\n".join(items)

    def __post_init__(self):
        """Pass."""
        self.ASSET_SCOPES = self.ASSET_SCOPES or {}

    def to_tablize(self) -> dict:
        """Pass."""
        ident = [
            f"Name: {self.name!r}",
            f"UUID: {self.uuid!r}",
            f"Description: {self.description!r}",
            f"Updated Date: {self.last_updated.isoformat()!r}",
            f"Updated User: {self.updated_user!r}",
        ]
        return {
            "Identifier": "\n".join(ident),
            "Associated Roles": "\n".join(self.associated_roles),
            "User Asset Scopes": "\n".join([x.name for x in self.users_scopes]),
            "Device Asset Scopes": "\n".join([x.name for x in self.devices_scopes]),
        }

    @staticmethod
    def find_scope(uuid: str, scopes: List[SavedQuery]) -> SavedQuery:
        """Pass."""
        try:
            return [x for x in scopes if x.uuid == uuid][0]
        except Exception:
            scopes = "\n\n" + "\n\n".join([str(x) for x in scopes])
            raise ApiError(f"Unable to find Saved Query UUID {uuid!r} in:{scopes}")

    @property
    def users_scopes(self) -> List[SavedQuery]:
        """Pass."""
        scopes = self.ASSET_SCOPES.get("users") or []
        return [self.find_scope(uuid=x, scopes=scopes) for x in self.users_queries]

    @property
    def devices_scopes(self) -> List[SavedQuery]:
        """Pass."""
        scopes = self.ASSET_SCOPES.get("devices") or []
        return [self.find_scope(uuid=x, scopes=scopes) for x in self.devices_queries]

    @property
    def scope_types(self) -> List[str]:
        """Pass."""
        return ["devices", "users"]

    def check_scope_type(self, scope_type: str):
        """Pass."""
        if scope_type not in self.scope_types:
            raise ApiError(f"Invalid scope Type {scope_type!r}, valids: {self.scope_types}")

    def update_scopes(
        self, scope_type: str, scopes: List[SavedQuery], append: bool = False, remove: bool = False
    ) -> List[str]:
        """Pass."""
        self.check_scope_type(scope_type)

        if (
            not isinstance(scopes, list)
            or not scopes
            or not all([isinstance(x, SavedQuery) for x in scopes])
        ):
            raise ApiError(f"Must supply at least one asset scope of type {scope_type}")

        scope_cache = self.ASSET_SCOPES.get(scope_type, [])
        scope_cache_ids = [x.uuid for x in scope_cache]
        scope_cache += [x for x in scopes if x.uuid not in scope_cache_ids]
        scope_ids = [x.uuid for x in scopes]
        queries_attr = f"{scope_type}_queries"
        queries_current = getattr(self, queries_attr)

        if remove:
            queries_new = [x for x in queries_current if x not in scope_ids]
        elif append:
            queries_new = queries_current + [x for x in scope_ids if x not in queries_current]
        else:
            queries_new = scope_ids

        setattr(self, queries_attr, queries_new)

        if not any([self.users_queries, self.devices_queries]):
            raise ApiError("Data Scopes must have a least one user or device Asset Scope")
        return queries_new


class DataScopeDetailsSchema(BaseSchemaJson):
    """Pass."""

    scopes = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Dict(), description="Data Scope objects"
    )
    settings = marshmallow_jsonapi.fields.Dict(description="Data Scopes settings")

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return DataScopeDetails

    class Meta:
        """Pass."""

        type_ = "data_scope_details_schema"


@dataclasses.dataclass
class DataScopeDetails(BaseModel):
    """Pass."""

    scopes: List[dict]
    settings: dict

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return DataScopeDetailsSchema

    def get_scopes(self, asset_scopes: Dict[str, List[SavedQuery]]) -> List[DataScope]:
        """Pass."""
        schema = DataScope.schema(many=True)
        objs = schema.load(self.scopes, unknown=marshmallow.INCLUDE)
        for obj in objs:
            obj.HTTP = self.HTTP
            obj.ASSET_SCOPES = asset_scopes
        return objs


class DataScopeCreateSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(description="Name of Data Scope")
    description = marshmallow_jsonapi.fields.Str(
        description="Description of Data Scope",
        load_default="",
        dump_default="",
        allow_none=True,
    )
    devices_queries = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(),
        description="Asset Scope UUIDs for type 'devices'",
    )
    users_queries = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(),
        description="Asset Scope UUIDs for type 'users'",
    )

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return DataScopeCreate

    class Meta:
        """Pass."""

        type_ = "data_scope_request_schema"


@dataclasses.dataclass
class DataScopeCreate(BaseModel):
    """Pass."""

    name: str
    devices_queries: List[str] = dataclasses.field(default_factory=list)
    users_queries: List[str] = dataclasses.field(default_factory=list)
    description: str = ""

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return DataScopeCreateSchema


class DataScopeUpdateSchema(BaseSchemaJson):
    """Pass."""

    uuid = marshmallow_jsonapi.fields.Str(description="UUID of Data Scope")
    name = marshmallow_jsonapi.fields.Str(description="Name of Data Scope")
    description = marshmallow_jsonapi.fields.Str(
        description="Description of Data Scope",
        load_default="",
        dump_default="",
        allow_none=True,
    )
    devices_queries = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(),
        description="Asset Scope UUIDs for type 'devices'",
    )
    users_queries = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(),
        description="Asset Scope UUIDs for type 'users'",
    )

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return DataScopeUpdate

    class Meta:
        """Pass."""

        type_ = "data_scope_request_schema"


@dataclasses.dataclass
class DataScopeUpdate(BaseModel):
    """Pass."""

    uuid: str
    name: str
    devices_queries: List[str] = dataclasses.field(default_factory=list)
    users_queries: List[str] = dataclasses.field(default_factory=list)
    description: str = ""

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return DataScopeUpdateSchema
