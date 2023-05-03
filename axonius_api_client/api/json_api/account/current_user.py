# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

from marshmallow_jsonapi import fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, SchemaDatetime, field_from_mm


class CurrentUserSchema(BaseSchemaJson):
    """Schema for receiving current user response.

    This schema does not match the REST API definition because it does not
    follow its own rules. email is defined as allow_none=False in REST API,
    however it can come back as None from REST API.

    Since it happened once, we are setting allow_none=True on all fields for
    safety since we get this object anytime str(Connect()) is called.
    """

    id = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    uuid = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    role_id = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    role_name = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    user_name = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    password = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    source = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    first_name = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    last_name = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    email = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    department = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    title = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    pic_name = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    predefined = SchemaBool(allow_none=True, load_default=False, dump_default=False)
    is_axonius_role = SchemaBool(allow_none=True, load_default=False, dump_default=False)
    interests = mm_fields.Dict(allow_none=True, load_default=dict, dump_default=dict)
    permissions = mm_fields.Dict(allow_none=True, load_default=dict, dump_default=dict)
    data_scope = mm_fields.Dict(allow_none=True, dump_default=dict, load_default=dict)
    allowed_scopes_impersonation = mm_fields.List(
        mm_fields.Str, allow_none=True, load_default=list, dump_default=list
    )
    timeout = mm_fields.Integer(allow_none=True, load_default=None, dump_default=None)
    last_updated = SchemaDatetime(allow_none=True, load_default=None, dump_default=None)
    last_login = SchemaDatetime(allow_none=True, load_default=None, dump_default=None)

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

    id: t.Optional[str] = field_from_mm(SCHEMA, "id")
    uuid: t.Optional[str] = field_from_mm(SCHEMA, "uuid")
    role_id: t.Optional[str] = field_from_mm(SCHEMA, "role_id")
    role_name: t.Optional[str] = field_from_mm(SCHEMA, "role_name")
    user_name: t.Optional[str] = field_from_mm(SCHEMA, "user_name")
    password: t.Optional[str] = field_from_mm(SCHEMA, "password")
    source: t.Optional[str] = field_from_mm(SCHEMA, "source")
    first_name: t.Optional[str] = field_from_mm(SCHEMA, "first_name")
    last_name: t.Optional[str] = field_from_mm(SCHEMA, "last_name")
    email: t.Optional[str] = field_from_mm(SCHEMA, "email")
    department: t.Optional[str] = field_from_mm(SCHEMA, "department")
    title: t.Optional[str] = field_from_mm(SCHEMA, "title")
    pic_name: t.Optional[str] = field_from_mm(SCHEMA, "pic_name")
    predefined: t.Optional[bool] = field_from_mm(SCHEMA, "predefined")
    is_axonius_role: t.Optional[bool] = field_from_mm(SCHEMA, "is_axonius_role")
    permissions: t.Optional[dict] = field_from_mm(SCHEMA, "permissions", repr=False)
    interests: t.Optional[dict] = field_from_mm(SCHEMA, "interests")
    data_scope: t.Optional[dict] = field_from_mm(SCHEMA, "data_scope")
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
    def last_login_seconds_ago(self) -> t.Optional[float]:
        """Get the number of seconds since last login."""
        delta = self.last_login_delta
        if isinstance(delta, datetime.timedelta):
            return round(delta.total_seconds(), 2)

    @property
    def last_login_delta(self) -> t.Optional[datetime.timedelta]:
        """Get the timedelta since last login."""
        from ....tools import dt_parse

        last_login = dt_parse(self.last_login, allow_none=True)
        if last_login:
            return datetime.datetime.now(datetime.timezone.utc) - last_login

    @property
    def str_connect(self) -> str:
        """Get a string for use in str for Connect."""
        return (
            f"User: {self.user_name!r}, Source: {self.source!r}, Role: {self.role_name!r}, "
            f"Last Login Delta: {self.last_login_delta}"
        )
