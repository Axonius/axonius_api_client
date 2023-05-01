# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ...constants.api import MAX_PAGE_SIZE, PAGE_SIZE
from ...tools import combo_dicts, parse_int_min_max
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, field_from_mm


class PaginationSchema(BaseSchema):
    """Schema for requests that use pagination."""

    offset = mm_fields.Integer(
        load_default=0,
        dump_default=0,
        description="Row start",
    )
    limit = mm_fields.Integer(
        load_default=MAX_PAGE_SIZE,
        dump_default=MAX_PAGE_SIZE,
        description=f"Page size (max: {MAX_PAGE_SIZE})",
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return PaginationRequest


PAGE_SCHEMA = PaginationSchema()


@dataclasses.dataclass
class PaginationRequest(BaseModel):
    """Model for requests that use pagination."""

    offset: t.Optional[int] = field_from_mm(PAGE_SCHEMA, "offset")
    limit: t.Optional[int] = field_from_mm(PAGE_SCHEMA, "limit")

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return PaginationSchema

    def set_offset(self, value: t.Optional[int]) -> int:
        """Set the offset (row start) for this request."""
        self.offset = parse_int_min_max(value=value, default=0, min_value=0, max_value=None)
        return self.offset

    def set_limit(self, value: t.Optional[int]) -> int:
        """Set the limit (page size) for this request."""
        self.limit = parse_int_min_max(
            value=value, default=PAGE_SIZE, min_value=1, max_value=MAX_PAGE_SIZE
        )
        return self.limit

    @classmethod
    def load_if_needed(cls, value: t.Any) -> t.Any:
        """Pass through if already an instance of this model, else load from dict."""
        if isinstance(value, cls):
            return value
        return cls(**combo_dicts(value))

    def __post_init__(self):
        """Dataclass post init."""
        self.set_offset(self.offset)
        self.set_limit(self.limit)


class ResourcesGetSchema(BaseSchemaJson):
    """Schema used for getting numerous object types throughout the API."""

    page = mm_fields.Nested(
        PaginationSchema(),
        load_default=PaginationRequest,
        dump_default=PaginationRequest,
        allow_none=True,
        description="Pagination parameters",
    )
    sort = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Field to sort by, prefix with '-' for descending",
    )
    search = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Search term",
    )
    filter = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Filter to limit results, aql-ish",
    )
    get_metadata = SchemaBool(
        load_default=True,
        dump_default=True,
        description="Include pagination metadata in response",
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return ResourcesGet

    class Meta:
        """JSONAPI config."""

        type_ = "resource_request_schema"


RESOURCES_GET_SCHEMA = ResourcesGetSchema()


@dataclasses.dataclass
class ResourcesGet(BaseModel):
    """Model used for getting numerous object types throughout the API."""

    page: t.Optional[t.Union[dict, PaginationRequest]] = field_from_mm(RESOURCES_GET_SCHEMA, "page")
    sort: t.Optional[str] = field_from_mm(RESOURCES_GET_SCHEMA, "sort")
    search: t.Optional[str] = field_from_mm(RESOURCES_GET_SCHEMA, "search")
    filter: t.Optional[str] = field_from_mm(RESOURCES_GET_SCHEMA, "filter")
    get_metadata: bool = field_from_mm(RESOURCES_GET_SCHEMA, "get_metadata")

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return ResourcesGetSchema

    def __post_init__(self):
        """Dataclass post init."""
        if isinstance(self.page, dict):
            self.page = PaginationRequest(**self.page)
        if not isinstance(self.page, PaginationRequest):
            self.page = PaginationRequest()


class ResourceDeleteSchema(BaseSchemaJson):
    """Schema used for deleting numerous object types throughout the API."""

    uuid = mm_fields.Str()

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return ResourceDelete


@dataclasses.dataclass
class ResourceDelete(BaseModel):
    """Model used for deleting numerous object types throughout the API."""

    uuid: str

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return ResourceDeleteSchema
