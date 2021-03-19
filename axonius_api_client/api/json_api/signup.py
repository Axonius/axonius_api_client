# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import Optional, Type

import marshmallow_jsonapi

from ..models import DataModel, DataSchema, DataSchemaJson
from .custom_fields import get_field_str_req


class SignupRequestSchema(DataSchemaJson):
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
    def _get_model_cls() -> type:
        """Pass."""
        return SignupRequest


@dataclasses.dataclass
class SignupRequest(DataModel):
    """Pass."""

    company_name: str
    contact_email: str
    new_password: str
    confirm_new_password: str
    user_name: str
    api_keys: bool = True

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return SignupRequestSchema


class SignupResponseSchema(DataSchemaJson):
    """Pass."""

    api_key = get_field_str_req()
    api_secret = get_field_str_req()

    class Meta:
        """Pass."""

        type_ = "signup_response_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return SignupResponse


@dataclasses.dataclass
class SignupResponse(DataModel):
    """Pass."""

    api_key: str
    api_secret: str

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return SignupResponseSchema
