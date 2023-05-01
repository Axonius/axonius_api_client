# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow
import marshmallow_jsonapi

from ...tools import is_str, json_load
from .base import BaseModel, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, SchemaPassword, get_field_dc_mm
from .system_roles import SystemRole


class SystemUserSchema(BaseSchemaJson):
    """Pass."""

    email = marshmallow_jsonapi.fields.Str(allow_none=True)
    first_name = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    last_login = SchemaDatetime()
    last_name = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    last_updated = SchemaDatetime()
    password = SchemaPassword(load_default="", dump_default="", allow_none=True)
    pic_name = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    role_id = marshmallow_jsonapi.fields.Str(required=True)
    role_name = marshmallow_jsonapi.fields.Str(
        load_default=None, dump_default=None, allow_none=True
    )
    title = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    department = marshmallow_jsonapi.fields.Str(
        load_default=None, dump_default=None, allow_none=True
    )
    source = marshmallow_jsonapi.fields.Str()
    user_name = marshmallow_jsonapi.fields.Str(required=True)
    uuid = marshmallow_jsonapi.fields.Str(required=True)
    ignore_role_assignment_rules = SchemaBool(
        load_default=False, dump_default=False, allow_none=True
    )
    allowed_scopes_impersonation = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(), load_default=list, dump_default=list
    )

    @staticmethod
    def get_model_cls() -> t.Any:
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

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return SystemUserUpdate

    @marshmallow.pre_load
    def pre_load_fix(self, data, **kwargs) -> t.Union[dict, BaseModel]:
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
class SystemUser(BaseModel):
    """Pass."""

    role_id: str
    user_name: str
    uuid: str

    email: t.Optional[str] = None
    first_name: t.Optional[str] = None
    id: t.Optional[str] = None
    last_login: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    last_name: t.Optional[str] = None
    last_updated: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    password: t.Optional[t.Union[t.List[str], str]] = None
    pic_name: t.Optional[str] = None
    role_name: t.Optional[str] = None
    title: t.Optional[str] = None
    department: t.Optional[str] = None
    source: t.Optional[str] = None
    ignore_role_assignment_rules: bool = False
    allowed_scopes_impersonation: t.List[str] = dataclasses.field(default_factory=list)
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
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

    @property
    def role_obj(self) -> SystemRole:
        """Pass."""
        if not hasattr(self, "_role_obj"):
            self._role_obj = self.HTTP.CLIENT.system_roles.get_cached_single(value=self.role_name)
        return self._role_obj

    def to_dict_old(self) -> dict:
        """Pass."""
        obj = self.to_dict()
        obj["role_obj"] = self.role_obj.to_dict_old()
        obj["role_name"] = self.role_obj["name"]
        obj["full_name"] = self.full_name
        return obj

    @property
    def user_source(self) -> str:
        """Pass."""
        return self.get_user_source(value=self)

    @classmethod
    def get_user_source(cls, value: t.Union[str, dict, "SystemUser"]) -> str:
        """Pass."""

        def add_part(part):
            if is_str(part):
                parts.append(part)

        parts = []
        if is_str(value):
            value = json_load(obj=value, error=False)

        if isinstance(value, str):
            add_part(value)
        elif isinstance(value, dict):
            add_part(value.get("user_name"))
            add_part(value.get("source"))
        elif isinstance(value, cls):
            add_part(value.user_name)
            add_part(value.source)
        return "/".join(parts)


@dataclasses.dataclass
class SystemUserUpdate(SystemUser):
    """Pass."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SystemUserUpdateSchema


class SystemUserCreateSchema(BaseSchemaJson):
    """Pass."""

    user_name = marshmallow_jsonapi.fields.Str(required=True)
    role_id = marshmallow_jsonapi.fields.Str(required=True)

    auto_generated_password = SchemaBool(load_default=False, dump_default=False)
    email = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    first_name = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    last_name = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    password = SchemaPassword(load_default="", dump_default="", allow_none=True)

    @staticmethod
    def get_model_cls() -> t.Any:
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
    email: t.Optional[str] = None
    first_name: t.Optional[str] = None
    last_name: t.Optional[str] = None
    password: t.Optional[str] = get_field_dc_mm(
        mm_field=SchemaPassword(load_default="", dump_default="", allow_none=True), default=""
    )

    def __post_init__(self):
        """Pass."""
        self.email = self.email or ""
        self.first_name = self.first_name or ""
        self.last_name = self.last_name or ""
        self.password = self.password or ""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SystemUserCreateSchema
