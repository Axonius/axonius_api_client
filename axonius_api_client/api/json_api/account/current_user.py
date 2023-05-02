# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

from marshmallow_jsonapi import fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, SchemaDatetime, field_from_mm


class CurrentUserSchema(BaseSchemaJson):
    """Schema for receiving current user response."""

    id = mm_fields.Str()
    uuid = mm_fields.Str()
    role_id = mm_fields.Str()
    role_name = mm_fields.Str()
    user_name = mm_fields.Str()
    password = mm_fields.Str()
    source = mm_fields.Str()
    first_name = mm_fields.Str()
    last_name = mm_fields.Str()
    email = mm_fields.Str()
    department = mm_fields.Str()
    title = mm_fields.Str()
    pic_name = mm_fields.Str()
    predefined = SchemaBool()
    is_axonius_role = SchemaBool()
    interests = mm_fields.Dict(load_default=dict, dump_default=dict)
    permissions = mm_fields.Dict(load_default=dict, dump_default=dict)
    data_scope = mm_fields.Dict(dump_default=dict, load_default=dict)
    allowed_scopes_impersonation = mm_fields.List(
        mm_fields.Str, load_default=list, dump_default=list
    )
    timeout = mm_fields.Integer(load_default=None, dump_default=None, alllow_none=True)
    last_updated = SchemaDatetime(load_default=None, dump_default=None, allow_none=True)
    last_login = SchemaDatetime(load_default=None, dump_default=None, allow_none=True)

    class Meta:
        """JSONAPI config."""

        type_ = "current_user_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return CurrentUser


SCHEMA = CurrentUserSchema()


@dataclasses.dataclass
class CurrentUser(BaseModel):
    """Model for receiving current user response."""

    id: str = field_from_mm(SCHEMA, "id")
    uuid: str = field_from_mm(SCHEMA, "uuid")
    role_id: str = field_from_mm(SCHEMA, "role_id")
    role_name: str = field_from_mm(SCHEMA, "role_name")
    user_name: str = field_from_mm(SCHEMA, "user_name")
    password: str = field_from_mm(SCHEMA, "password")
    source: str = field_from_mm(SCHEMA, "source")
    first_name: str = field_from_mm(SCHEMA, "first_name")
    last_name: str = field_from_mm(SCHEMA, "last_name")
    email: str = field_from_mm(SCHEMA, "email")
    department: str = field_from_mm(SCHEMA, "department")
    title: str = field_from_mm(SCHEMA, "title")
    pic_name: str = field_from_mm(SCHEMA, "pic_name")
    predefined: bool = field_from_mm(SCHEMA, "predefined")
    is_axonius_role: bool = field_from_mm(SCHEMA, "is_axonius_role")
    permissions: dict = field_from_mm(SCHEMA, "permissions", repr=False)
    interests: dict = field_from_mm(SCHEMA, "interests")
    data_scope: dict = field_from_mm(SCHEMA, "data_scope")
    allowed_scopes_impersonation: t.List[str] = field_from_mm(
        SCHEMA, "allowed_scopes_impersonation"
    )
    timeout: t.Optional[int] = field_from_mm(SCHEMA, "timeout")
    last_updated: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "last_updated")
    last_login: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "last_login")

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[CurrentUserSchema] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CurrentUserSchema

    @property
    def last_login_seconds_ago(self) -> float:
        """Get the number of seconds since last login."""
        return round(self.last_login_delta.total_seconds(), 2)

    @property
    def last_login_delta(self) -> datetime.timedelta:
        """Get the timedelta since last login."""
        return datetime.datetime.now(datetime.timezone.utc) - self.last_login

    @property
    def str_connect(self) -> str:
        """Get a string for use in str for Connect."""
        return (
            f"User: {self.user_name!r}, Source: {self.source!r}, Role: {self.role_name!r}, "
            f"Last Login Delta: {self.last_login_delta}"
        )
