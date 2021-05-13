# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type, Union

import marshmallow
import marshmallow_jsonapi

from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, SchemaPassword, get_field_dc_mm


class SystemUserSchema(BaseSchemaJson):
    """Pass."""

    email = marshmallow_jsonapi.fields.Str(allow_none=True)
    first_name = marshmallow_jsonapi.fields.Str()
    last_login = SchemaDatetime()
    last_name = marshmallow_jsonapi.fields.Str()
    last_updated = SchemaDatetime()
    password = SchemaPassword(default="", allow_none=True)
    pic_name = marshmallow_jsonapi.fields.Str()
    role_id = marshmallow_jsonapi.fields.Str(required=True)
    source = marshmallow_jsonapi.fields.Str()
    user_name = marshmallow_jsonapi.fields.Str(required=True)
    uuid = marshmallow_jsonapi.fields.Str(required=True)

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SystemUser

    class Meta:
        """Pass."""

        type_ = "users_details_schema"


class SystemUserUpdateSchema(SystemUserSchema):
    """Pass."""

    last_login = SchemaDatetime(allow_none=True)

    class Meta:
        """Pass."""

        type_ = "users_schema"

    @marshmallow.pre_load
    def pre_load_fix(self, data, **kwargs) -> Union[dict, BaseModel]:
        """Pass."""
        data["email"] = data.get("email", "") or ""
        data["first_name"] = data.get("first_name", "") or ""
        data["last_name"] = data.get("last_name", "") or ""
        data["password"] = data.get("password", "") or ""
        return data

    @marshmallow.post_dump
    def post_dump_fixit(self, data: dict, **kwargs) -> dict:
        """Pass."""
        # PBUG: these should really just be ignored by rest api
        data.pop("last_updated", None)
        data.pop("last_login", None)
        data.pop("uuid", None)

        return data


@dataclasses.dataclass
class PasswordLinkCreateRequest(BaseModel):
    """Pass."""

    user_id: str
    user_name: str


@dataclasses.dataclass
class PasswordLinkSendRequest(BaseModel):
    """Pass."""

    email: str
    user_id: str
    invite: bool = False


@dataclasses.dataclass
class PasswordLinkSendResponse(BaseModel):
    """Pass."""

    user_name: str


@dataclasses.dataclass
class PasswordTokenValidateRequest(BaseModel):
    """Pass."""

    token: bool

    def dump_request_params(self, **kwargs) -> Optional[dict]:
        """Pass."""
        return None


@dataclasses.dataclass
class PasswordTokenValidateResponse(BaseModel):
    """Pass."""

    valid: bool


@dataclasses.dataclass
class SystemUser(BaseModel):
    """Pass."""

    role_id: str
    user_name: str
    uuid: str

    email: str = None
    first_name: Optional[str] = None
    id: Optional[str] = None
    last_login: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    last_name: Optional[str] = None
    last_updated: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    password: Optional[Union[List[str], str]] = None
    pic_name: Optional[str] = None
    source: Optional[str] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SystemUserSchema

    @property
    def full_name(self) -> str:
        """Pass."""
        return " ".join([x for x in [self.first_name, self.last_name] if x])

    def __post_init__(self):
        """Pass."""
        if self.id is None and self.uuid is not None:
            self.id = self.uuid

    def to_dict_old(self, system_roles: List[dict]) -> dict:
        """Pass."""
        system_role = [x for x in system_roles if x["uuid"] == self.role_id][0]
        obj = self.to_dict()
        obj["role_obj"] = system_role
        obj["role_name"] = system_role["name"]
        obj["full_name"] = self.full_name
        return obj


class SystemUserCreateSchema(BaseSchemaJson):
    """Pass."""

    user_name = marshmallow_jsonapi.fields.Str(required=True)
    role_id = marshmallow_jsonapi.fields.Str(required=True)

    auto_generated_password = SchemaBool(default=False)
    email = marshmallow_jsonapi.fields.Str(default="", allow_none=True)
    first_name = marshmallow_jsonapi.fields.Str(default="", allow_none=True)
    last_name = marshmallow_jsonapi.fields.Str(default="", allow_none=True)
    password = SchemaPassword(default="", allow_none=True)

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SystemUserCreate

    class Meta:
        """Pass."""

        type_ = "create_user_schema"

    @marshmallow.validates_schema
    def validate_fields(self, data, **kwargs):
        """Pass."""
        errors = {}
        if not data.get("password") and not data.get("auto_generated_password"):
            errors["password"] = "Must supply a password if auto_generated_password is False"
            raise marshmallow.ValidationError(errors)


@dataclasses.dataclass
class SystemUserCreate(BaseModel):
    """Pass."""

    user_name: str
    role_id: str

    auto_generated_password: bool = False
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = get_field_dc_mm(
        mm_field=SchemaPassword(default="", allow_none=True), default=""
    )

    def __post_init__(self):
        """Pass."""
        self.email = self.email or ""
        self.first_name = self.first_name or ""
        self.last_name = self.last_name or ""
        self.password = self.password or ""

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SystemUserCreateSchema
