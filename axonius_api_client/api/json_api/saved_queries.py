# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import re
import textwrap
from typing import ClassVar, List, Optional, Pattern, Tuple, Type, Union

import marshmallow
import marshmallow_jsonapi

from ...constants.api import GUI_PAGE_SIZES
from ...constants.general import STR_RE_LISTY
from ...data import BaseEnum
from ...exceptions import ApiAttributeTypeError, ApiError, NotFoundError
from ...parsers.tables import tablize
from ...tools import coerce_bool, coerce_int, dt_now, dt_parse, listify
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, get_schema_dc
from .generic import PrivateRequest, PrivateRequestSchema
from .resources import PaginationRequest, PaginationSchema, ResourcesGet, ResourcesGetSchema


class AccessMode(BaseEnum):
    """Pass."""

    public: str = "Public"
    private: str = "Private"
    restricted: str = "Restricted"
    shared: str = "Shared"

    @classmethod
    def get_default(cls) -> "AccessMode":
        """Pass."""
        return cls.public

    @classmethod
    def key_mode(self) -> str:
        """Pass."""
        return "mode"

    @classmethod
    def get_default_access(cls) -> dict:
        """Pass."""
        return {cls.key_mode(): cls.get_default().value}

    @classmethod
    def get_access_bool(cls, value: bool) -> dict:
        """Pass."""
        if value:
            return {cls.key_mode(): cls.private.value}
        else:
            return {cls.key_mode(): cls.public.value}


class SavedQueryGetSchema(ResourcesGetSchema):
    """Pass."""

    folder_id = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    creator_ids = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    used_in = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    get_view_data = SchemaBool(load_default=True, dump_default=True)
    include_usage = SchemaBool(load_default=False, dump_default=False)

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SavedQueryGet

    class Meta:
        """Pass."""

        type_ = "request_views_schema"


class QueryHistorySchema(BaseSchemaJson):
    """Pass."""

    query_id = marshmallow_jsonapi.fields.Str(allow_none=False)
    saved_query_name = marshmallow_jsonapi.fields.Str(
        load_default=None, dump_default=None, allow_none=True
    )
    saved_query_tags = marshmallow.fields.List(marshmallow_jsonapi.fields.Str())
    start_time = SchemaDatetime(allow_none=True)
    end_time = SchemaDatetime(allow_none=True)
    duration = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    run_by = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    run_from = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    execution_source = marshmallow_jsonapi.fields.Dict(
        load_default=None, dump_default=None, allow_none=True
    )
    status = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    module = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    results_count = marshmallow.fields.Integer(
        load_default=None, dump_default=None, allow_none=True
    )

    class Meta:
        """Pass."""

        type_ = "entities_queries_history_response_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return QueryHistory

    @classmethod
    def validate_attr_excludes(cls) -> List[str]:
        """Pass."""
        return ["document_meta", "id"]


class QueryHistoryRequestSchema(BaseSchemaJson):
    """Pass."""

    folder_id = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    run_by = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    run_from = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    modules = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    saved_query_name_term = marshmallow_jsonapi.fields.Str(allow_none=True)
    date_from = SchemaDatetime(allow_none=True)
    date_to = SchemaDatetime(allow_none=True)
    page = marshmallow_jsonapi.fields.Nested(PaginationSchema)
    sort = marshmallow_jsonapi.fields.Str(
        allow_none=True,
        load_default=None,
        dump_default=None,
        validate=QueryHistorySchema.validate_attr,
    )
    search = marshmallow_jsonapi.fields.Str(allow_none=True, load_default="", dump_default="")
    filter = marshmallow_jsonapi.fields.Str(allow_none=True, load_default="", dump_default="")

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return QueryHistoryRequest

    class Meta:
        """Pass."""

        type_ = "entities_queries_history_request_schema"

    @classmethod
    def validate_attrs(cls) -> dict:
        """Pass."""
        return QueryHistorySchema.validate_attrs()


class SavedQuerySchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    always_cached = SchemaBool(load_default=False, dump_default=False)
    asset_scope = SchemaBool(load_default=False, dump_default=False)
    private = SchemaBool(load_default=False, dump_default=False)
    description = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    view = marshmallow_jsonapi.fields.Dict(allow_none=True, load_default={}, dump_default={})
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

    # 2022-09-02
    folder_id = marshmallow_jsonapi.fields.Str(allow_none=True, load_default="", dump_default="")

    # 2022-09-02
    last_run_time = SchemaDatetime(allow_none=True, load_default=None, dump_default=None)

    # 2022-09-02
    created_by = marshmallow_jsonapi.fields.Str(
        allow_none=True, load_default=None, dump_default=None
    )

    # 2022-09-02
    # used_in = marshmallow_jsonapi.fields.List()

    # 2022-09-02
    module = marshmallow_jsonapi.fields.Str(allow_none=True, load_default=None, dump_default=None)
    # 2022-08-22
    access = marshmallow_jsonapi.fields.Dict(
        load_default=AccessMode.get_default_access(), dump_default=AccessMode.get_default_access()
    )

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
    access = marshmallow_jsonapi.fields.Dict(
        load_default=AccessMode.get_default_access(), dump_default=AccessMode.get_default_access()
    )
    # WIP: folders
    folder_id = marshmallow_jsonapi.fields.Str(allow_none=True, load_default="", dump_default="")

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
    view: Optional[dict] = dataclasses.field(default_factory=dict, metadata={"update": True})
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

    # 2022-09-02
    folder_id: str = ""

    # 2022-09-02
    last_run_time: Optional[datetime.datetime] = dataclasses.field(
        default=None,
        metadata={
            "dataclasses_json": {"mm_field": SchemaDatetime(allow_none=True)},
        },
    )

    # 2022-09-02
    created_by: Optional[str] = None

    # 2022-09-02
    module: Optional[str] = None

    # 2022-09-02
    used_in: Optional[List[str]] = dataclasses.field(default_factory=list)
    access: dict = dataclasses.field(default_factory=AccessMode.get_default_access)

    document_meta: Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Pass."""
        self.uuid = self.uuid or self.id
        self.folder_id = self.folder_id or ""

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
    access: Optional[dict] = None
    folder_id: str = ""

    def __post_init__(self):
        """Pass."""
        if not (isinstance(self.access, dict) and self.access):
            self.access = AccessMode.get_access_bool(self.private)
        self.folder_id = self.folder_id or ""

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


@dataclasses.dataclass
class SavedQueryGet(ResourcesGet):
    """Pass."""

    folder_id: str = ""
    creator_ids: Optional[List[str]] = dataclasses.field(default_factory=list)
    used_in: Optional[List[str]] = dataclasses.field(default_factory=list)
    get_view_data: bool = True
    include_usage: bool = False

    def __post_init__(self):
        """Pass."""
        self.folder_id = self.folder_id or ""
        self.creator_ids = self.creator_ids or []
        self.used_in = self.used_in or []
        self.page = self.page if self.page else PaginationRequest()

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SavedQueryGetSchema


@dataclasses.dataclass
class QueryHistoryRequest(BaseModel):
    """Pass."""

    run_by: Optional[List[str]] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="run_by",
        default_factory=list,
    )
    run_from: Optional[List[str]] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="run_from",
        default_factory=list,
    )
    modules: Optional[List[str]] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="modules",
        default_factory=list,
    )
    tags: Optional[List[str]] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="tags",
        default_factory=list,
    )
    saved_query_name_term: Optional[str] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="saved_query_name_term",
        default=None,
    )
    date_from: Optional[datetime.datetime] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="date_from",
        default=None,
    )
    date_to: Optional[datetime.datetime] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="date_to",
        default=None,
    )
    page: Optional[PaginationRequest] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="page",
        default_factory=PaginationRequest,
    )
    search: Optional[str] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="search",
        default="",
    )
    filter: Optional[str] = get_schema_dc(
        schema=QueryHistoryRequestSchema,
        key="filter",
        default=None,
    )

    def __post_init__(self):
        """Pass."""
        self.run_by = self.run_by or []
        self.run_from = self.run_from or []
        self.modules = self.modules or []
        self.tags = self.tags or []
        self.page = self.page if self.page else PaginationRequest()

    def set_sort(self, value: Optional[str] = None, descending: bool = False) -> Optional[str]:
        """Pass."""
        if isinstance(value, str) and value:
            value = QueryHistorySchema.validate_attr(value=value, exc_cls=NotFoundError)
            value = self._prepend_sort(value=value, descending=descending)
        else:
            value = None

        self.sort = value
        return value

    def set_name_term(self, value: Optional[str] = None) -> Optional[str]:
        """Pass."""
        if isinstance(value, str) and value:
            self.saved_query_name_term = value
        else:
            value = None
            self.saved_query_name_term = value
        return value

    def set_date(
        self,
        date_start: Optional[datetime.datetime] = None,
        date_end: Optional[datetime.datetime] = None,
    ) -> Tuple[Optional[datetime.datetime], Optional[datetime.datetime]]:
        """Pass."""
        if date_end and not date_start:
            raise ApiError("date_start must also be supplied when date_end is supplied")

        if date_start:
            date_start = dt_parse(date_start)
            if date_end:
                date_end = dt_parse(date_end)
            else:
                date_end = dt_now()
        return (date_start, date_end)

    @classmethod
    def get_list_props(cls) -> List[str]:
        """Pass."""
        return [x.name for x in cls._get_fields() if x.type == Optional[List[str]]]

    def set_list(
        self,
        prop: str,
        values: Optional[List[str]] = None,
        enum: Optional[List[str]] = None,
        enum_callback: Optional[callable] = None,
    ) -> List[str]:
        """Pass."""

        def err(check, use_enum):
            valids = [{f"Valid {prop} values": x} for x in use_enum]
            err = f"No {prop} matching {check!r} found out of {len(use_enum)} items"
            err_table = tablize(value=valids, err=err)
            raise NotFoundError(err_table)

        props = self.get_list_props()
        if prop not in props:
            raise ApiError(f"Invalid list property {prop}, valids: {props}")

        values = listify(values)
        use_enum = None
        if isinstance(enum, list) and enum:
            use_enum = enum
        elif callable(enum_callback):
            use_enum = enum_callback()

        matches = []
        for value in values:
            if isinstance(value, str):
                check = value
                if check.startswith("~"):
                    check = re.compile(check[1:])
            elif isinstance(value, Pattern):
                check = value
            else:
                raise ApiError(
                    f"Value must be {STR_RE_LISTY}, not type={type(value)}, value={value!r}"
                )

            if isinstance(use_enum, list) and use_enum:
                if isinstance(check, str):
                    if check not in use_enum:
                        err(check=check, use_enum=use_enum)
                    matches.append(check)
                elif isinstance(check, Pattern):
                    re_matches = [x for x in use_enum if check.search(x)]
                    if not re_matches:
                        err(check=check, use_enum=use_enum)
                    matches += re_matches
            else:
                if isinstance(check, str):
                    matches.append(check)

        self._log.debug(f"Resolved {prop} values {values} to matches {matches}")
        setattr(self, prop, matches)
        return matches

    def set_search_filter(
        self, search: Optional[str] = None, filter: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """Pass."""
        values = [search, filter]
        is_strs = [isinstance(x, str) and x for x in values]
        if any(is_strs) and not all(is_strs):
            raise ApiError(f"Only search or filter supplied, must supply both: {values}")
        if not all(is_strs):
            search = ""
            filter = None
        self.search = search
        self.filter = filter
        return (search, filter)

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return QueryHistoryRequestSchema


@dataclasses.dataclass
class QueryHistory(BaseModel):
    """Pass."""

    query_id: str = get_schema_dc(schema=QueryHistorySchema, key="query_id")
    saved_query_name: Optional[str] = get_schema_dc(
        schema=QueryHistorySchema, key="saved_query_name", default=None
    )
    saved_query_tags: Optional[List[str]] = get_schema_dc(
        schema=QueryHistorySchema, key="saved_query_tags", default=None
    )
    start_time: Optional[datetime.datetime] = get_schema_dc(
        schema=QueryHistorySchema, key="start_time", default=None
    )
    end_time: Optional[datetime.datetime] = get_schema_dc(
        schema=QueryHistorySchema, key="end_time", default=None
    )
    duration: Optional[str] = get_schema_dc(schema=QueryHistorySchema, key="duration", default=None)
    run_by: Optional[str] = get_schema_dc(schema=QueryHistorySchema, key="run_by", default=None)
    run_from: Optional[str] = get_schema_dc(schema=QueryHistorySchema, key="run_from", default=None)
    execution_source: Optional[dict] = get_schema_dc(
        schema=QueryHistorySchema, key="execution_source", default=None
    )
    status: Optional[str] = get_schema_dc(schema=QueryHistorySchema, key="status", default=None)
    module: Optional[str] = get_schema_dc(schema=QueryHistorySchema, key="module", default=None)
    results_count: Optional[int] = get_schema_dc(
        schema=QueryHistorySchema, key="results_count", default=None
    )

    @staticmethod
    def get_schema_cls():
        """Pass."""
        return QueryHistorySchema

    @property
    def name(self) -> Optional[str]:
        """Pass."""
        return self.saved_query_name

    @property
    def tags(self) -> Optional[str]:
        """Pass."""
        return self.saved_query_tags

    @property
    def asset_type(self) -> Optional[str]:
        """Pass."""
        return self.execution_source.get("entity_type")

    @property
    def component(self) -> Optional[str]:
        """Pass."""
        return self.execution_source.get("component")

    def __str__(self) -> List[str]:
        """Pass."""

        def getval(prop):
            value = getattr(self, prop, None)
            if value is not None and not isinstance(value, (str, int, float, bool)):
                value = str(value)
            return repr(value)

        vals = ", ".join([f"{p}={getval(p)}" for p in self._props_details()])
        return f"{self.__class__.__name__}({vals})"

    def __repr__(self):
        """Pass."""
        return self.__str__()

    def to_csv(self) -> dict:
        """Pass."""

        def getval(prop):
            value = getattr(self, prop, None)
            if isinstance(value, list):
                value = "\n".join(value)
            return value

        return {k: getval(k) for k in self._props_csv()}

    def to_tablize(self) -> dict:
        """Pass."""

        def getval(prop, width=30):
            value = getattr(self, prop, None)
            if isinstance(width, int) and len(str(value)) > width:
                value = textwrap.fill(value, width=width)
            prop = prop.replace("_", " ").title()
            return f"{prop}: {value}"

        def getvals(props, width=30):
            return "\n".join([getval(prop=p, width=width) for p in props])

        tags = "\nTags:\n  " + "\n  ".join(self.tags or [])
        return {
            "Details": getvals(self._props_details(), None) + tags,
            "Results": getvals(self._props_timings() + self._props_results(), None),
        }

    @classmethod
    def _props_csv(cls) -> List[str]:
        """Pass."""
        return cls._props_custom() + [
            x for x in cls._get_field_names() if x not in cls._props_skip()
        ]

    @classmethod
    def _props_details(cls) -> List[str]:
        """Pass."""
        return [x for x in cls._props_custom() if x not in ["tags"]] + [
            x for x in cls._get_field_names() if x not in cls._props_details_excludes()
        ]

    @classmethod
    def _props_details_excludes(cls) -> List[str]:
        """Pass."""
        return cls._props_custom() + cls._props_skip() + cls._props_timings() + cls._props_results()

    @classmethod
    def _props_timings(cls) -> List[str]:
        """Pass."""
        return ["start_time", "end_time", "duration"]

    @classmethod
    def _props_skip(cls) -> List[str]:
        """Pass."""
        return ["execution_source", "document_meta", "saved_query_name", "saved_query_tags"]

    @classmethod
    def _props_custom(cls) -> List[str]:
        """Pass."""
        return ["name", "tags"]

    @classmethod
    def _props_results(cls) -> List[str]:
        """Pass."""
        return ["status", "results_count"]


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
