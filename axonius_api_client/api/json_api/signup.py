# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import Optional, Type

import marshmallow_jsonapi

from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import get_field_str_req


class SignupRequestSchema(BaseSchemaJson):
    """Pass."""

    company_name = get_field_str_req()
    new_password = get_field_str_req()
    confirm_new_password = get_field_str_req()
    contact_email = marshmallow_jsonapi.fields.Email(required=True)
    user_name = get_field_str_req()
    api_keys = marshmallow_jsonapi.fields.Bool(missing=True)

    class Meta:
        """Pass."""

        type_ = "signup_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SignupRequest


class SystemStatusSchema(BaseSchemaJson):
    """Pass."""

    msg = marshmallow_jsonapi.fields.Str()
    is_ready = marshmallow_jsonapi.fields.Bool()
    status_code = marshmallow_jsonapi.fields.Int()

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SystemStatus

    class Meta:
        """Pass."""

        type_ = "machine_status_schema"


@dataclasses.dataclass
class SignupRequest(BaseModel):
    """Pass."""

    company_name: str
    contact_email: str
    new_password: str
    confirm_new_password: str
    user_name: str
    api_keys: bool = True

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SignupRequestSchema


class SignupResponseSchema(BaseSchemaJson):
    """Pass."""

    api_key = get_field_str_req()
    api_secret = get_field_str_req()

    class Meta:
        """Pass."""

        type_ = "signup_response_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SignupResponse


@dataclasses.dataclass
class SignupResponse(BaseModel):
    """Pass."""

    api_key: str
    api_secret: str

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SignupResponseSchema


@dataclasses.dataclass
class SystemStatus(BaseModel):
    """Pass."""

    msg: str
    is_ready: bool
    status_code: int

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SystemStatusSchema

    def __str__(self) -> str:
        """Pass."""
        msg = self.msg or "none"
        return f"System status - ready: {self.is_ready}, message: {msg} (code: {self.status_code})"
