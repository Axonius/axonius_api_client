# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import Optional, Type

import marshmallow
import marshmallow_jsonapi

from ...constants.api import MAX_PAGE_SIZE
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, get_field_dc_mm


class PaginationSchema(marshmallow.Schema):
    """Pass."""

    offset = marshmallow_jsonapi.fields.Integer(default=0, missing=0)
    limit = marshmallow_jsonapi.fields.Integer(default=140, missing=140)


@dataclasses.dataclass
class PaginationRequest(BaseModel):
    """Pass."""

    offset: Optional[int] = 0
    """Row to start from"""

    limit: Optional[int] = MAX_PAGE_SIZE
    """Number of rows to return"""

    def __post_init__(self):
        """Pass."""
        try:
            self.limit = int(self.limit)
        except Exception:
            self.limit = MAX_PAGE_SIZE
        finally:
            if self.limit > MAX_PAGE_SIZE or self.limit < 1:
                self.limit = MAX_PAGE_SIZE

        try:
            self.offset = int(self.offset)
        except Exception:
            self.offset = 0
        finally:
            if self.offset < 0:
                self.offset = 0


@dataclasses.dataclass
class PageSortRequest(BaseModel):
    """Data attributes for pagination and sort."""

    sort: Optional[str] = None
    """Field to sort on and direction to sort.

    not used by api client (sort using client side logic)

    examples:
        for descending: "-field"
        for ascending: "field"
    """

    page: Optional[PaginationRequest] = get_field_dc_mm(
        marshmallow_jsonapi.fields.Nested(PaginationSchema), default=None
    )
    """Row to start at and number of rows to return.

    examples:
        in get request: page[offset]=0&page[limit]=2000
        in post request: {"data": {"attributes": {"page": {"offset": 0, "limit": 2000}}}
    """
    # FYI: with out using mm_field metadata for nested schemas for dataclasses_json,
    # the mm field that dataclasses_json dynamically creates produces warnings
    # about using deprecated additional_meta args

    get_metadata: bool = True
    """Return pagination metadata in response."""

    def __post_init__(self):
        """Pass."""
        if self.page is None:
            self.page = PaginationRequest()


class ResourcesGetSchema(BaseSchemaJson):
    """Pass."""

    sort = marshmallow_jsonapi.fields.Str()
    page = marshmallow_jsonapi.fields.Nested(PaginationSchema)
    search = marshmallow_jsonapi.fields.Str(default="", missing="")
    get_metadata = SchemaBool(missing=True)

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return ResourcesGet

    class Meta:
        """Pass."""

        type_ = "resource_base_schema"


@dataclasses.dataclass
class ResourcesGet(PageSortRequest):
    """Request attributes for getting resources."""

    search: Optional[str] = None
    """AQL search term

    not used by api client (filter using client side logic)

    examples:
        (name == regex("test", "i"))
        (name == regex("test", "i")) and tags in ["Linux"]
    """

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return ResourcesGetSchema


@dataclasses.dataclass
class ResourceDelete(BaseModel):
    """Pass."""

    uuid: str
