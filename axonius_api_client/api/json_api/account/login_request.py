# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from marshmallow_jsonapi import fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, field_from_mm


class LoginRequestSchema(BaseSchemaJson):
    """Schema for issuing a login request."""

    user_name = mm_fields.Str(
        allow_none=True,
        dump_default=None,
        load_default=None,
        description="Axonius User Name",
    )
    password = mm_fields.Str(
        allow_none=True,
        dump_default=None,
        load_default=None,
        description="Axonius Password",
    )
    saml_token = mm_fields.Str(
        allow_none=True,
        dump_default=None,
        load_default=None,
        description="SAML token from 2FA negotiation",
    )
    remember_me = SchemaBool(
        load_default=False,
        dump_default=False,
        description="Used for browser controls",
    )
    eula_agreed = SchemaBool(
        load_default=False,
        dump_default=False,
        description="EULA has been agreed to by user",
    )

    class Meta:
        """Pass."""

        type_ = "login_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return LoginRequest


SCHEMA: BaseSchemaJson = LoginRequestSchema()


@dataclasses.dataclass
class LoginRequest(BaseModel):
    """Model for issuing a login request."""

    user_name: t.Optional[str] = field_from_mm(SCHEMA, "user_name")
    password: t.Optional[str] = field_from_mm(SCHEMA, "password")
    saml_token: t.Optional[str] = field_from_mm(SCHEMA, "saml_token")
    remember_me: bool = field_from_mm(SCHEMA, "remember_me")
    eula_agreed: bool = field_from_mm(SCHEMA, "eula_agreed")

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return LoginRequestSchema
