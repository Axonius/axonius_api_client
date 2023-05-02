# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, field_from_mm


class SignupRequestSchema(BaseSchemaJson):
    """Schema for performing an initial signup request."""

    company_name = mm_fields.Str(required=False, description="Company name (Optional)")
    new_password = mm_fields.Str(required=True, description="Admin user password")
    confirm_new_password = mm_fields.Str(
        required=True, description="Admin user password confirmation"
    )
    contact_email = mm_fields.Email(required=True, description="Admin email address")
    user_name = mm_fields.Str(required=True, description="Admin user name")
    api_keys = SchemaBool(
        required=False,
        load_default=True,
        dump_default=True,
        descripton="Whether to return the API key and secret",
    )

    class Meta:
        """JSONAPI config."""

        type_ = "signup_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return SignupRequest


SCHEMA: BaseSchemaJson = SignupRequestSchema()


@dataclasses.dataclass
class SignupRequest(BaseModel):
    """Model for performing an initial signup request."""

    company_name: str = field_from_mm(SCHEMA, "company_name")
    contact_email: str = field_from_mm(SCHEMA, "contact_email")
    new_password: str = field_from_mm(SCHEMA, "new_password")
    confirm_new_password: str = field_from_mm(SCHEMA, "confirm_new_password")
    user_name: str = field_from_mm(SCHEMA, "user_name")
    api_keys: bool = field_from_mm(SCHEMA, "api_keys")

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return SignupRequestSchema
