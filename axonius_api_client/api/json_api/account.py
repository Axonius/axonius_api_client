# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow

from ...exceptions import AuthError
from .base import BaseModel, BaseSchemaJson
from .custom_fields import SchemaBool
from .generic import Metadata, MetadataSchema


class LoginRequestSchema(BaseSchemaJson):
    """Schema for issuing a login request."""

    user_name = marshmallow.fields.Str(
        allow_none=True,
        dump_default=None,
        load_default=None,
        description="Axonius User Name",
    )
    password = marshmallow.fields.Str(
        allow_none=True,
        dump_default=None,
        load_default=None,
        description="Axonius Password",
    )
    saml_token = marshmallow.fields.Str(
        allow_none=True,
        dump_default=None,
        load_default=None,
        description="SAML token from 2FA negotiation",
    )
    remember_me = SchemaBool(
        load_default=False, dump_default=False, description="Used for browser controls"
    )
    eula_agreed = SchemaBool(
        load_default=False, dump_default=False, description="EULA has been agreed to by user"
    )

    class Meta:
        """Pass."""

        type_ = "login_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return LoginRequest


LOGIN_REQUEST_SCHEMA = LoginRequestSchema()


@dataclasses.dataclass
class LoginRequest(BaseModel):
    """Model for issuing a login request."""

    user_name: t.Optional[str] = None
    password: t.Optional[str] = None
    saml_token: t.Optional[str] = None
    remember_me: bool = False
    eula_agreed: bool = False

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

        field: marshmallow.Field = LOGIN_REQUEST_SCHEMA.declared_fields[attr]
        description: str = field.metadata.get("description", f"{attr}")
        msgs: t.List[str] = [
            f"Value provided for {description} is not a non-empty string"
            f"Provided type {type(value)}, value: {value!r}"
        ]
        raise AuthError(msgs)

    def check_credentials(self):
        """Check that username and password are not empty."""
        self._check_credential(attr="user_name")
        self._check_credential(attr="password")


class LoginResponseSchema(MetadataSchema):
    """Schema for receiving a login response."""

    class Meta:
        """Pass."""

        type_ = "metadata_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return LoginResponse


@dataclasses.dataclass
class LoginResponse(Metadata):
    """Model for receiving a login response."""

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return LoginResponseSchema

    @property
    def access_token(self) -> str:
        """Get the Access token for use in auth header."""
        return self.document_meta["access_token"]

    @property
    def refresh_token(self) -> str:
        """Get the Refresh token for use in auth header."""
        return self.document_meta["refresh_token"]

    @property
    def authorization(self) -> str:
        """Get the value to use in the authorization header."""
        return f"Bearer {self.access_token}"
