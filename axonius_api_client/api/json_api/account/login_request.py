# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from marshmallow_jsonapi import fields as mm_fields

from ....exceptions import AuthError
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

    def __post_init__(self):
        """Post init."""
        self.check_credentials()

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return LoginRequestSchema

    def _check_credential(self, attr: str) -> str:
        """Check that a credential is a non-empty string."""
        value: t.Any = getattr(self, attr)

        if isinstance(value, str) and value.strip():
            value = value.strip()
            setattr(self, attr, value)
            return value

        field: mm_fields.Field = SCHEMA.declared_fields[attr]
        description: str = field.metadata.get("description", f"{attr}")
        msgs: t.List[str] = [
            f"Value provided for {description} is not a non-empty string",
            f"Provided type {type(value)}, value: {value!r}",
        ]
        raise AuthError(msgs)

    def check_credentials(self):
        """Check that username and password are not empty."""
        self._check_credential(attr="user_name")
        self._check_credential(attr="password")
