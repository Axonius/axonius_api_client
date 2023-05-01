# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import field_from_mm


class SignupResponseSchema(BaseSchemaJson):
    """Schema for response from performing initial signup."""

    api_key = mm_fields.Str(description="Value to use in 'api-key' header for API requests")
    api_secret = mm_fields.Str(description="Value to use in 'api-secret' header for API requests")

    class Meta:
        """JSONAPI config."""

        type_ = "signup_response_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return SignupResponse


SCHEMA: BaseSchemaJson = SignupResponseSchema()


@dataclasses.dataclass
class SignupResponse(BaseModel):
    """Model for response from performing initial signup."""

    api_key: str = field_from_mm(SCHEMA, "api_key")
    api_secret: str = field_from_mm(SCHEMA, "api_secret")
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return SignupResponseSchema
