# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow
import marshmallow_jsonapi

from ...exceptions import ApiError
from ...tools import json_load
from .base import BaseModel, BaseSchemaJson
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
        """Get the username of the user that last updated this object."""
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

    associated_roles: t.List[str] = dataclasses.field(default_factory=list)
    users_queries: t.List[str] = dataclasses.field(default_factory=list)
    devices_queries: t.List[str] = dataclasses.field(default_factory=list)

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    def __str__(self) -> str:
        """Pass."""
        items = [
            f"Name: {self.name!r}",
            f"UUID: {self.uuid!r}",
            f"Description: {self.description!r}",
            f"Associated Roles: {self.associated_roles}",
            f"User Asset Scopes: {self.users_scopes_names}",
            f"Device Asset Scopes: {self.devices_scopes_names}",
            f"Updated Date: {self.last_updated.isoformat()!r}",
            f"Updated User: {self.updated_user!r}",
        ]
        return "\n".join(items)

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
            "User Asset Scopes": "\n".join(self.users_scopes_names),
            "Device Asset Scopes": "\n".join(self.devices_scopes_names),
        }

    @property
    def users_scopes_names(self) -> t.List[str]:
        """Pass."""
        return [x.name for x in self.users_scopes]

    @property
    def devices_scopes_names(self) -> t.List[str]:
        """Pass."""
        return [x.name for x in self.devices_scopes]

    @property
    def users_scopes(self) -> t.List[SavedQuery]:
        """Pass."""
        if not hasattr(self, "_user_scopes"):
            self._user_scopes = [
                self.HTTP.CLIENT.users.saved_query.get_cached_single(value=x)
                for x in self.users_queries
            ]
        return self._user_scopes

    @property
    def devices_scopes(self) -> t.List[SavedQuery]:
        """Pass."""
        if not hasattr(self, "_device_scopes"):
            self._device_scopes = [
                self.HTTP.CLIENT.devices.saved_query.get_cached_single(value=x)
                for x in self.devices_queries
            ]
        return self._device_scopes

    @property
    def scope_types(self) -> t.List[str]:
        """Pass."""
        return ["devices", "users"]

    def check_scope_type(self, scope_type: str):
        """Pass."""
        if scope_type not in self.scope_types:
            raise ApiError(f"Invalid scope Type {scope_type!r}, valids: {self.scope_types}")

    def update_scopes(
        self,
        scope_type: str,
        scopes: t.List[SavedQuery],
        append: bool = False,
        remove: bool = False,
    ) -> t.List[str]:
        """Pass."""
        self.check_scope_type(scope_type)

        if (
            not isinstance(scopes, list)
            or not scopes
            or not all([isinstance(x, SavedQuery) for x in scopes])
        ):
            raise ApiError(f"Must supply at least one asset scope of type {scope_type}")

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

        if not any([getattr(self, f"{x}_queries", []) for x in self.scope_types]):
            raise ApiError(
                f"Data Scopes must have a least one Asset Scope of any types: {self.scope_types}"
            )
        return queries_new


class DataScopeDetailsSchema(BaseSchemaJson):
    """Pass."""

    scopes = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Dict(), description="Data Scope objects"
    )
    settings = marshmallow_jsonapi.fields.Dict(description="Data Scopes settings")

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return DataScopeDetails

    class Meta:
        """Pass."""

        type_ = "data_scope_details_schema"


@dataclasses.dataclass
class DataScopeDetails(BaseModel):
    """Pass."""

    scopes: t.List[dict]
    settings: dict
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return DataScopeDetailsSchema

    def get_scopes(self) -> t.List[DataScope]:
        """Pass."""
        schema = DataScope.schema(many=True, unknown=marshmallow.INCLUDE)
        objs = schema.load(self.scopes, unknown=marshmallow.INCLUDE)
        for obj in objs:
            obj.HTTP = self.HTTP
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
    def get_model_cls() -> t.Any:
        """Pass."""
        return DataScopeCreate

    class Meta:
        """Pass."""

        type_ = "data_scope_request_schema"


@dataclasses.dataclass
class DataScopeCreate(BaseModel):
    """Pass."""

    name: str
    devices_queries: t.List[str] = dataclasses.field(default_factory=list)
    users_queries: t.List[str] = dataclasses.field(default_factory=list)
    description: str = ""

    @staticmethod
    def get_schema_cls() -> t.Any:
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
    def get_model_cls() -> t.Any:
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
    devices_queries: t.List[str] = dataclasses.field(default_factory=list)
    users_queries: t.List[str] = dataclasses.field(default_factory=list)
    description: str = ""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return DataScopeUpdateSchema
