# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import ClassVar, Dict, List, Optional, Type

import marshmallow
import marshmallow_jsonapi

from ...tools import json_load
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaDatetime
from .saved_queries import SavedQuery


@dataclasses.dataclass
class DataScope(BaseModel):
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
        user_scopes = [x.name for x in self.user_scopes]
        device_scopes = [x.name for x in self.device_scopes]
        items = [
            f"name={self.name!r}",
            f"uuid={self.uuid!r}",
            f"description={self.description!r}",
            f"associated_roles={self.associated_roles}",
            f"user_scopes={user_scopes}",
            f"device_scopes={device_scopes}",
        ]
        return "\n".join(items)

    @property
    def updated_user_obj(self) -> dict:
        """Pass."""
        if not hasattr(self, "_updated_user_obj"):
            self._updated_user_obj = json_load(self.updated_by)
        return self._updated_user_obj

    @property
    def updated_user_name(self) -> str:
        """Get the user name of the user that last updated this set."""
        return self.updated_user_obj.get("user_name", "")

    @property
    def updated_user_source(self) -> str:
        """Get the source of the user that last updated this set."""
        return self.updated_user_obj.get("source", "")

    @property
    def updated_user_first_name(self) -> str:
        """Get the first name of the user that last updated this set."""
        return self.updated_user_obj.get("first_name", "")

    @property
    def updated_user_last_name(self) -> str:
        """Get the last name of the user that last updated this set."""
        return self.updated_user_obj.get("last_name", "")

    @property
    def updated_user_full_name(self) -> str:
        """Get the first and last name of the user that last updated this set."""
        return " ".join(
            [x for x in [self.updated_user_first_name, self.updated_user_last_name] if x]
        )

    @property
    def updated_user(self) -> str:
        """Pass."""
        return f"{self.updated_user_source}/{self.updated_user_name}"

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
            "User Asset Scopes": "\n".join([x.name for x in self.user_scopes]),
            "Device Asset Scopes": "\n".join([x.name for x in self.device_scopes]),
        }

    @property
    def user_scopes(self) -> List[SavedQuery]:
        """Pass."""
        return [x for x in self.ASSET_SCOPES["users"] if x.uuid in self.users_queries]

    @property
    def device_scopes(self) -> List[SavedQuery]:
        """Pass."""
        return [x for x in self.ASSET_SCOPES["devices"] if x.uuid in self.devices_queries]


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
