# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import textwrap
from typing import ClassVar, List, Optional, Type, Union

import marshmallow
import marshmallow_jsonapi

from ...constants.api import GUI_PAGE_SIZES
from ...exceptions import ApiAttributeTypeError, ApiError
from ...tools import coerce_bool, coerce_int, listify
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime
from .generic import PrivateRequest, PrivateRequestSchema


class SavedQuerySchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    always_cached = SchemaBool(load_default=False, dump_default=False)
    asset_scope = SchemaBool(load_default=False, dump_default=False)
    private = SchemaBool(load_default=False, dump_default=False)
    description = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    view = marshmallow_jsonapi.fields.Dict()
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    predefined = SchemaBool(load_default=False, dump_default=False)
    date_fetched = marshmallow_jsonapi.fields.Str(
        allow_none=True, load_default=None, dump_default=None
    )
    is_asset_scope_query_ready = SchemaBool()
    is_referenced = SchemaBool()
    query_type = marshmallow_jsonapi.fields.Str(
        allow_none=True, load_default="saved", dump_default="saved"
    )
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    timestamp = marshmallow_jsonapi.fields.Str(allow_none=True)
    last_updated = SchemaDatetime(allow_none=True)
    updated_by = marshmallow_jsonapi.fields.Str(
        allow_none=True, load_default=None, dump_default=None
    )
    user_id = marshmallow_jsonapi.fields.Str(allow_none=True, load_default=None, dump_default=None)
    uuid = marshmallow_jsonapi.fields.Str(allow_none=True, load_default=None, dump_default=None)
    # WIP: folders
    # folder_id = marshmallow_jsonapi.fields.Str(
    #     allow_none=True, load_default=None, dump_default=None
    # )

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SavedQuery

    class Meta:
        """Pass."""

        type_ = "views_details_schema"


class SavedQueryDeleteSchema(PrivateRequestSchema):
    """Pass."""

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SavedQueryDelete

    class Meta:
        """Pass."""

        type_ = "delete_view_schema"


class FoldersResponseSchema(BaseSchemaJson):
    """Pass."""

    folders = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return FoldersResponse

    class Meta:
        """Pass."""

        type_ = "queries_folders_response_schema"


class SavedQueryCreateSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    view = marshmallow_jsonapi.fields.Dict()
    description = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    always_cached = SchemaBool(load_default=False, dump_default=False)
    private = SchemaBool(load_default=False, dump_default=False)
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    asset_scope = SchemaBool(load_default=False, dump_default=False)
    # WIP: folders
    # folder_id = marshmallow_jsonapi.fields.Str(
    #     allow_none=True, load_default=None, dump_default=None
    # )

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SavedQueryCreate

    class Meta:
        """Pass."""

        type_ = "views_schema"


class SavedQueryMixins:
    """Pass."""

    GET_ATTRS: List[str] = [
        "name",
        "view",
        "description",
        "always_cached",
        "asset_scope",
        "private",
        "tags",
    ]

    def get_attrs(self, attrs: Optional[List[str]] = None) -> dict:
        """Pass."""
        attrs = listify(attrs) or self.GET_ATTRS
        return {x: getattr(self, x) for x in attrs if isinstance(x, str) and hasattr(self, x)}

    def set_name(self, value: str):
        """Set the name of this SQ."""
        if not isinstance(value, str) or (isinstance(value, str) and not value.strip()):
            raise ApiAttributeTypeError(f"Value must be a non-empty string, not {value!r}")
        self.name = value

    def set_description(self, value: str):
        """Set the description of this SQ."""
        if not isinstance(value, str):
            raise ApiAttributeTypeError(f"Value must be a string, not {value!r}")
        self.description = value

    def set_tags(self, value: List[str]):
        """Set the tags for this SQ."""
        value = listify(value)
        if not all([isinstance(x, str) and x.strip() for x in value]):
            raise ApiAttributeTypeError(f"Tags must be a list of non-empty strings, not {value!r}")

        self.tags = value

    @property
    def fields(self) -> List[str]:
        """Get the fields for this SQ."""
        return self.view.get("fields") or []

    @fields.setter
    def fields(self, value: List[str]):
        """Set the fields for this SQ."""
        value = listify(value)
        if not all([isinstance(x, str) and x.strip() for x in value]):
            raise ApiAttributeTypeError(f"Fields {value} must be a list of non-empty strings")

        self.view["fields"] = value

    @property
    def _query(self) -> dict:
        """Get the query object from the view object."""
        return self.view.get("query") or {}

    @property
    def _sort(self) -> dict:
        """Get the sort object from the view object."""
        return self.view.get("sort") or {}

    @property
    def sort_field(self) -> str:
        """Get the field the SQ should be sorted on."""
        return self._sort.get("field") or ""

    @sort_field.setter
    def sort_field(self, value: str):
        if not isinstance(value, str):
            raise ApiAttributeTypeError(f"Sort field {value!r} must be a string")
        self._sort["field"] = value

    @property
    def sort_descending(self) -> bool:
        """Get whether the sort_field should be sorted descending or not."""
        return self._sort.get("desc", True)

    @sort_descending.setter
    def sort_descending(self, value: bool):
        """Set whether the sort_field should be sorted descending or not."""
        self._sort["desc"] = coerce_bool(obj=value, errmsg="Sort descending must be a boolean")

    @property
    def query(self) -> str:
        """Get the AQL for this SQ."""
        return self._query.get("filter") or ""

    @query.setter
    def query(self, value: str):
        """Set the AQL for this SQ."""
        self._query["filter"] = value

    @property
    def query_expr(self) -> str:
        """Get the expr AQL for this SQ."""
        return self._query.get("onlyExpressionsFilter") or ""

    @query_expr.setter
    def query_expr(self, value: str):
        """Set the expr AQL for this SQ."""
        self._query["onlyExpressionsFilter"] = value

    @staticmethod
    def reindex_expressions(value: List[dict]) -> List[dict]:
        """Reindex the GUI query wizard expressions."""
        if isinstance(value, list):
            for idx, item in enumerate(value):
                if not isinstance(item, dict):
                    raise ApiAttributeTypeError(f"Expression must be a dict {item}")
                if idx == 0:
                    item.pop("i", None)
                else:
                    item["i"] = idx
        return value

    @property
    def expressions(self) -> List[dict]:
        """Get the query wizard expressions for this SQ."""
        return self._query.get("expressions") or []

    @expressions.setter
    def expressions(self, value: List[dict]):
        """Set the query wizard expressions for this SQ."""
        if not isinstance(value, list) or not all([isinstance(x, dict) and x for x in value]):
            raise ApiAttributeTypeError(
                f"Expressions {value} must be a list of non-empty dictionaries"
            )
        self.reindex_expressions(value=value)
        self._query["expressions"] = value

    @property
    def page_size(self) -> int:
        """Get the page size for this SQ."""
        return self.view.get("pageSize", GUI_PAGE_SIZES[0])

    @page_size.setter
    def page_size(self, value: int):
        value = coerce_int(
            obj=value,
            valid_values=GUI_PAGE_SIZES,
            errmsg=f"Invalid page size {value!r} for Saved Queries",
        )

        self.view["pageSize"] = value


@dataclasses.dataclass
class SavedQuery(BaseModel, SavedQueryMixins):
    """Pass."""

    id: str = dataclasses.field(metadata={"update": False})
    name: str = dataclasses.field(metadata={"min_length": 1, "update": True})
    view: dict = dataclasses.field(metadata={"update": True})
    query_type: str = dataclasses.field(default="saved", metadata={"update": True})
    updated_by: Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    user_id: Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    uuid: Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    date_fetched: Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    timestamp: Optional[str] = dataclasses.field(default=None, metadata={"update": False})
    last_updated: Optional[datetime.datetime] = dataclasses.field(
        default=None,
        metadata={
            "dataclasses_json": {"mm_field": SchemaDatetime(allow_none=True)},
        },
    )
    always_cached: bool = dataclasses.field(default=False, metadata={"update": True})
    asset_scope: bool = dataclasses.field(default=False, metadata={"update": True})
    private: bool = dataclasses.field(default=False, metadata={"update": True})
    description: Optional[str] = dataclasses.field(default="", metadata={"update": True})
    tags: List[str] = dataclasses.field(default_factory=list, metadata={"update": True})
    predefined: bool = dataclasses.field(default=False, metadata={"update": False})
    is_asset_scope_query_ready: bool = dataclasses.field(default=False, metadata={"update": False})
    is_referenced: bool = dataclasses.field(default=False, metadata={"update": False})
    # WIP: folders
    # folder_id: Optional[str] = None
    document_meta: Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Pass."""
        self.uuid = self.uuid or self.id

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SavedQuerySchema

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "name",
            "uuid",
            "description",
            "tags",
            "query",
            "fields",
            "last_updated",
            "private",
            "always_cached",
            "is_referenced",
            "asset_scope",
            "is_asset_scope_query_ready",
        ]

    @property
    def last_updated_str(self) -> str:
        """Get the last updated in str format."""
        return (
            self.last_updated.strftime("%Y-%m-%dT%H:%M:%S%z")
            if isinstance(self.last_updated, datetime.datetime)
            else self.last_updated
        )

    @property
    def flags(self) -> dict:
        """Get the flags for this SQ."""
        return {
            "predefined": self.predefined,
            "referenced": self.is_referenced,
            "private": self.private,
            "always_cached": self.always_cached,
            "asset_scope": self.asset_scope,
            "asset_scope_ready": self.is_asset_scope_query_ready,
        }

    @property
    def flags_txt(self) -> List[str]:
        """Get the text version of flags for this SQ."""
        return [f"{k}: {v}" for k, v in self.flags.items()]

    def to_tablize(self) -> dict:
        """Get tablize-able repr of this obj."""
        details = self.flags_txt + [
            f"page_size: {self.page_size}",
            f"updated: {self.last_updated_str}",
        ]
        ret = {}
        ret["Name/UUID"] = textwrap.fill(f"NAME={self.name}\nUUID={self.uuid}", width=30)
        ret["Description"] = textwrap.fill(self.description or "", width=30)
        ret["Tags"] = "\n".join(listify(self.tags))
        ret["Details"] = "\n".join(details)
        return ret


@dataclasses.dataclass
class SavedQueryCreate(BaseModel, SavedQueryMixins):
    """Pass."""

    name: str = dataclasses.field(metadata={"min_length": 1})
    view: dict  # TODO: add model
    description: Optional[str] = dataclasses.field(default="")
    always_cached: bool = dataclasses.field(default=False)
    asset_scope: bool = dataclasses.field(default=False)
    private: bool = dataclasses.field(default=False)
    tags: List[str] = dataclasses.field(default_factory=list)
    # WIP: folders
    # folder_id: Optional[str] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SavedQueryCreateSchema


@dataclasses.dataclass
class SavedQueryDelete(PrivateRequest):
    """Pass."""

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SavedQueryDeleteSchema


# WIP: folders
FOLDER_SEP: str = "//"


# WIP: folders
@dataclasses.dataclass
class Folder(BaseModel):  # pragma: no cover
    """Pass."""

    _id: str
    children_ids: List[str]
    depth: int
    name: str
    root_type: str
    created_at: datetime.datetime = dataclasses.field(
        metadata={"dataclasses_json": {"mm_field": SchemaDatetime()}}
    )
    updated_at: datetime.datetime = dataclasses.field(
        metadata={"dataclasses_json": {"mm_field": SchemaDatetime()}}
    )
    path: List[str]
    children: Optional[List[dict]] = dataclasses.field(default_factory=list)
    root_id: Optional[str] = None
    created_by: Optional[str] = None
    parent_id: Optional[str] = None
    read_only: bool = False

    PARENT: ClassVar[Optional[Union["Folder", "FoldersResponse"]]] = None

    @property
    def id(self) -> str:
        """Pass."""
        return self._id

    @property
    def path_str(self) -> str:
        """Pass."""
        return f" {FOLDER_SEP} ".join(self.path)

    @property
    def children_count(self) -> int:
        """Pass."""
        return len(self.children_ids)

    @property
    def models(self) -> List["Folder"]:
        """Pass."""
        schema = self.schema(many=True)
        items = schema.load(self.children, unknown=marshmallow.INCLUDE)
        for item in items:
            item.HTTP = self.HTTP
            item.PARENT = self
        return items

    def find_folder(self, value: str) -> "Folder":
        """Pass."""
        err = f"No folder named {value!r} found under {self.path_str!r}"
        if not self.children:
            raise ApiError(f"{err}No folders exist under {self.path_str!r}")

        for model in self.models:
            if model.name == value:
                return model

        valids = "\n" + "\n".join([str(x) for x in self.models])
        raise ApiError(f"{err}, valids:{valids}")

    def __str__(self) -> str:
        """Pass."""
        children = [x.name for x in self.models]
        items = [
            f"id: {self.id!r}",
            f"name: {self.name!r}",
            f"path: {self.path_str!r}",
            f"children: {children}",
        ]
        items = ", ".join(items)
        return f"Folder({items})"

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()


# WIP: folders
@dataclasses.dataclass
class FoldersResponse(BaseModel):  # pragma: no cover
    """Pass."""

    folders: List[dict]

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return FoldersResponseSchema

    @property
    def models(self) -> List[Folder]:
        """Pass."""
        schema = Folder.schema(many=True)
        items = schema.load(self.folders, unknown=marshmallow.INCLUDE)
        for item in items:
            item.HTTP = self.HTTP
            item.PARENT = self
        return items

    def find_folder(self, value: str) -> "Folder":
        """Pass."""
        for model in self.models:
            if model.name == value:
                return model

        valids = "\n" + "\n".join([str(x) for x in self.models])
        raise ApiError(f"No root folder named {value!r} found, valids:{valids}")

    def search(self, value: Union[str, List[str]]) -> Folder:
        """Find a folder by path."""
        if isinstance(value, str):
            value = [x.strip() for x in value.split(FOLDER_SEP) if x.strip()]

        if not isinstance(value, list) and value and all([isinstance(x, str) and x for x in value]):
            msg = (
                f"Invalid folder search value {value!r} ({type(value)})\n"
                f"Folder search value must be a list of str or a str separated by {FOLDER_SEP!r}"
            )
            raise ApiError(msg)

        folder = None
        for item in value:
            folder = folder.find_folder(value=item) if folder else self.find_folder(value=item)
        return folder

    def get_tree(self, models: Optional[List["Folder"]] = None):
        """Pass."""
        models = self.models if models is None else models

        items = []
        for model in models:
            items.append(f"{model.path_str}")
            items += self.get_tree(models=model.models)
        return items

    def __str__(self) -> str:
        """Pass."""
        items = ",\n".join(
            [f"Folder(name={x.name!r}, children={[y.name for y in x.models]})" for x in self.models]
        )
        return items

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()
