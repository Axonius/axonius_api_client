# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields

from ...constants.api import MAX_PAGE_SIZE, PAGE_SIZE
from ...tools import parse_int_min_max
from .base import BaseModel, BaseSchemaJson
from .custom_fields import SchemaBool


class PaginationSchema(marshmallow.Schema):
    """Pass."""

    offset = mm_fields.Integer(load_default=0, dump_default=0)
    limit = mm_fields.Integer(load_default=MAX_PAGE_SIZE, dump_default=MAX_PAGE_SIZE)


@dataclasses.dataclass
class PaginationRequest(BaseModel):
    """Pass."""

    offset: t.Optional[int] = 0
    """Row to start from"""

    limit: t.Optional[int] = MAX_PAGE_SIZE
    """Number of rows to return"""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None

    @property
    def page_size(self) -> t.Optional[int]:
        """Pass."""
        return self.limit

    @page_size.setter
    def page_size(self, value: t.Optional[int]):
        """Pass."""
        self.limit = parse_int_min_max(
            value=value, default=PAGE_SIZE, min_value=1, max_value=MAX_PAGE_SIZE
        )

    @property
    def row_start(self) -> t.Optional[int]:
        """Pass."""
        return self.offset

    @row_start.setter
    def row_start(self, value: t.Optional[int]):
        """Pass."""
        self.offset = parse_int_min_max(value=value, default=0, min_value=0, max_value=None)

    def __post_init__(self):
        """Pass."""
        self.row_start = self.limit
        self.page_size = self.offset


@dataclasses.dataclass
class PageSortRequest(BaseModel):
    """Data attributes for pagination and sort."""

    sort: t.Optional[str] = None
    """Field to sort on and direction to sort.

    not used by api client (sort using client side logic)

    examples:
        for descending: "-field"
        for ascending: "field"
    """

    page: t.Optional[PaginationRequest] = dataclasses.field(
        default=None,
        metadata={
            "dataclasses_json": {"mm_field": mm_fields.Nested(PaginationSchema())},
        },
    )
    """Row to start at and number of rows to return.

    examples:
        in get request: page[offset]=0&page[limit]=2000
        in post request: {"data": {"attributes": {"page": {"offset": 0, "limit": 2000}}}
    """
    # FYI: without using mm_field metadata for nested schemas for dataclasses_json,
    # the mm field that dataclasses_json dynamically creates produces warnings
    # about using deprecated additional_meta args

    get_metadata: bool = True
    """Return pagination metadata in response."""

    def __post_init__(self):
        """Pass."""
        self.page = self.page if self.page else PaginationRequest()

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


class ResourcesGetSchema(BaseSchemaJson):
    """Pass."""

    sort = mm_fields.Str(allow_none=True, load_default=None, dump_default=None)
    page = mm_fields.Nested(PaginationSchema())
    search = mm_fields.Str(load_default="", dump_default="")
    filter = mm_fields.Str(allow_none=True, load_default="", dump_default="")
    get_metadata = SchemaBool(load_default=True, dump_default=True)

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return ResourcesGet

    class Meta:
        """Pass."""

        type_ = "resource_request_schema"


@dataclasses.dataclass
class ResourcesGet(PageSortRequest):
    """Request attributes for getting resources."""

    search: str = dataclasses.field(
        default="",
        metadata={
            "dataclasses_json": {"mm_field": mm_fields.Str(load_default="", dump_default="")},
        },
    )
    """AQL search term

    not used by api client (filter using client side logic)

    examples:
        (name == regex("test", "i"))
        (name == regex("test", "i")) and tags in ["Linux"]
    """
    filter: t.Optional[str] = dataclasses.field(
        default=None,
        metadata={
            "dataclasses_json": {
                "mm_field": mm_fields.Str(allow_none=True, load_default="", dump_default="")
            },
        },
    )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return ResourcesGetSchema


@dataclasses.dataclass
class ResourceDelete(BaseModel):
    """Pass."""

    uuid: str

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None
