# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type, Union

import marshmallow
import marshmallow_jsonapi

from ...constants.api import MAX_PAGE_SIZE, PAGE_SIZE
from ...exceptions import ApiError, StopFetch
from ...http import Http
from ...tools import dt_parse, dt_sec_ago, json_dump, listify
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, get_field_dc_mm
from .generic import DictValue
from .resources import PaginationRequest, PaginationSchema


class ModifyTagsSchema(BaseSchemaJson):
    """Pass."""

    entities = marshmallow_jsonapi.fields.Dict()
    labels = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    filter = marshmallow_jsonapi.fields.Str(default="", missing="", allow_none=True)

    class Meta:
        """Pass."""

        type_ = "add_tags_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return ModifyTags


@dataclasses.dataclass
class ModifyTags(BaseModel):
    """Pass."""

    labels: List[str] = dataclasses.field(default_factory=list)
    entities: dict = dataclasses.field(default_factory=dict)
    filter: Optional[str] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return ModifyTagsSchema


class AssetMixins:
    """Pass."""

    def set_history(
        self,
        history: Union[str, datetime.timedelta, datetime.datetime],
        history_dates: DictValue,
        asset_type: str,
    ) -> str:
        """Pass."""
        if not history:
            return

        history = self._history_dt_fmt(dt=history)

        valid_dates = history_dates.value[asset_type]

        if history not in valid_dates:
            known = "\n  " + "\n  ".join(list(valid_dates))
            expl = "known history dates"
            err = f"Unknown history date {history!r}"
            msg = f"{err}, {expl}: {known}\n{err}, see above for {expl}"
            raise ApiError(msg)

        self.history = valid_dates[history]
        return self.history

    @staticmethod
    def _history_dt_fmt(
        dt: Union[str, datetime.timedelta, datetime.datetime], tmpl: str = "%Y-%m-%d"
    ) -> str:
        """Parse a string into the format used by the REST API.

        Args:
            dt: date time to parse using :meth:`dt_parse`
            tmpl: strftime template to convert dt into
        """
        valid_fmts = [
            "YYYY-MM-DD",
            "YYYYMMDD",
        ]
        try:
            dt = dt_parse(obj=dt)
            return dt.strftime(tmpl)
        except Exception:
            vtype = type(dt).__name__
            valid = "\n - " + "\n - ".join(valid_fmts)
            msg = f"Could not parse date {dt!r} of type {vtype} try a string like:{valid}"
            raise ApiError(msg)


class AssetRequestSchema(BaseSchemaJson):
    """Pass."""

    always_cached_query = SchemaBool(missing=False)
    use_cache_entry = SchemaBool(missing=False)
    include_details = SchemaBool(missing=False)
    include_notes = SchemaBool(missing=False)
    get_metadata = SchemaBool(missing=True)
    use_cursor = SchemaBool(missing=True)

    history = marshmallow_jsonapi.fields.Str(missing=None, allow_none=True)
    filter = marshmallow_jsonapi.fields.Str(default="", missing="", allow_none=True)
    cursor_id = marshmallow_jsonapi.fields.Str(missing=None, allow_none=True)
    sort = marshmallow_jsonapi.fields.Str(missing=None, allow_none=True)

    excluded_adapters = marshmallow_jsonapi.fields.Dict(missing={}, allow_none=True)
    field_filters = marshmallow_jsonapi.fields.Dict(missing={}, allow_none=True)
    fields = marshmallow_jsonapi.fields.Dict(missing={}, allow_none=True)

    page = marshmallow_jsonapi.fields.Nested(PaginationSchema)

    class Meta:
        """Pass."""

        type_ = "entity_request_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return AssetRequest

    @marshmallow.post_dump
    def post_dump_process(self, data, **kwargs) -> dict:
        """Pass."""
        data = {k: v for k, v in data.items() if v is not None}
        return data


@dataclasses.dataclass
class AssetRequest(BaseModel, AssetMixins):
    """Pass."""

    always_cached_query: bool = False
    use_cache_entry: bool = False
    include_details: bool = False
    include_notes: bool = False
    get_metadata: bool = True
    use_cursor: bool = True

    history: Optional[str] = None
    filter: Optional[str] = None
    cursor_id: Optional[str] = None
    sort: Optional[str] = None

    excluded_adapters: Optional[dict] = dataclasses.field(default_factory=dict)
    field_filters: Optional[dict] = dataclasses.field(default_factory=dict)
    fields: Optional[dict] = dataclasses.field(default_factory=dict)

    page: Optional[PaginationRequest] = get_field_dc_mm(
        marshmallow_jsonapi.fields.Nested(PaginationSchema), default=None
    )

    def __post_init__(self):
        """Pass."""
        self.excluded_adapters = self.excluded_adapters or {}
        self.field_filters = self.field_filters or {}
        self.fields = self.fields or {}
        self.page = self.page or PaginationRequest()

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return AssetRequestSchema

    def set_fields(self, asset_type: str, fields: List[str]):
        """Pass."""
        self.fields = {asset_type: listify(fields)}

    def set_sort(self, asset_type: str, field: str, descending: bool = False):
        """Pass."""
        if isinstance(field, str):
            field = field[1:] if field.startswith("-") else field
            field = f"-{field}" if descending else field
        else:
            field = None
        self.sort = field

    def set_page(self, limit: int = 0, offset: int = PAGE_SIZE):
        """Pass."""
        self.page = PaginationRequest(limit=limit, offset=offset)


@dataclasses.dataclass
class AssetsPage(BaseModel):
    """Pass."""

    assets: Optional[List[dict]] = dataclasses.field(default_factory=list)
    meta: Optional[dict] = dataclasses.field(default_factory=dict)
    empty_response: bool = False

    @classmethod
    def load_response(cls, data: dict, http: Http, api_endpoint, **kwargs):
        """Pass."""
        cls._check_version(data=data, api_endpoint=api_endpoint)
        empty = data.get("data") is None
        assets = [x["attributes"] for x in data.get("data") or []]
        meta = data.get("meta") or {}
        new_data = {"assets": assets, "meta": meta, "empty_response": empty}
        schema = cls.schema()
        return cls._load_schema(schema=schema, data=new_data, http=http, api_endpoint=api_endpoint)

    def __str__(self):
        """Pass."""
        other_meta = {k: v for k, v in self.meta.items() if k not in ["page"]}
        other_meta = [f"meta[{k}]={v}" for k, v in other_meta.items()]
        page_attrs = [f"{k}={getattr(self, k, None)}" for k in self.page_attrs]
        attrs = ", ".join(page_attrs + other_meta)
        return f"{self.__class__.__name__}({attrs})"

    def __repr__(self):
        """Pass."""
        return self.__str__()

    @property
    def page_attrs(self) -> List[str]:
        """Pass."""
        return [
            "page_number",
            "pages_total",
            "pages_left",
            "page_size",
            "asset_count_left",
            "asset_count_page",
            "asset_count_total",
        ]

    @property
    def cursor(self) -> str:
        """Pass."""
        return self.meta.get("cursor") or ""

    @property
    def page(self) -> dict:
        """Pass."""
        return self.meta.get("page") or {}

    @property
    def page_number(self) -> int:
        """Pass."""
        return self.page.get("number")

    @property
    def page_size(self) -> int:
        """Pass."""
        return self.page.get("size")

    @property
    def pages_total(self) -> int:
        """Pass."""
        return self.page.get("totalPages")

    @property
    def pages_left(self) -> int:
        """Pass."""
        return (self.pages_total or 0) - (self.page_number or 0)

    @property
    def asset_count_left(self) -> int:
        """Pass."""
        return self.asset_count_total

    @property
    def asset_count_total(self) -> int:
        """Pass."""
        return self.page.get("totalResources")

    @property
    def asset_count_page(self) -> int:
        """Pass."""
        return len(self.assets)

    @classmethod
    def create_state(
        cls,
        max_pages: int = 0,
        max_rows: int = 0,
        page_sleep: int = 0,
        page_size: int = PAGE_SIZE,
        page_start: int = 0,
        row_start: int = 0,
        initial_count: int = 0,
    ) -> dict:
        """Pass."""

        def check_int(value, default=0, min_value=None, max_value=None):
            if not isinstance(value, int):
                value = default

            if min_value is not None and value < min_value:
                value = default

            if max_value is not None and value > max_value:
                value = default

            return value

        max_rows = check_int(value=max_rows, default=0, min_value=0)
        max_pages = check_int(value=max_pages, default=0, min_value=0)
        page_start = check_int(value=page_start, default=0, min_value=0)
        row_start = check_int(value=row_start, default=0, min_value=0)
        page_size = check_int(
            value=page_size, default=PAGE_SIZE, min_value=1, max_value=MAX_PAGE_SIZE
        )
        page_sleep = check_int(value=page_sleep, default=0, min_value=0)

        if max_rows and max_rows < page_size:
            page_size = max_rows

        if page_start and not row_start:
            row_start = page_start * page_size

        state = {
            "max_pages": max_pages,
            "max_rows": max_rows,
            "page_cursor": None,
            "page_sleep": page_sleep,
            "page_size": page_size,
            "page_loop": 1,
            "page_number": 0,
            "page_start": page_start,
            "pages_to_fetch_left": 0,
            "pages_to_fetch_total": 0,
            "page": {},
            "rows_to_fetch_left": 0,
            "rows_to_fetch_total": 0,
            "rows_fetched_this_page": 0,
            "rows_fetched_total": 0,
            "rows_offset": row_start,
            "rows_initial_count": initial_count,
            "rows_processed_total": 0,
            "fetch_seconds_total": 0,
            "fetch_seconds_this_page": 0,
            "stop_fetch": False,
            "stop_msg": None,
        }
        return state

    def process_page(self, state: dict, start_dt: datetime.datetime, apiobj) -> dict:
        """Pass."""
        apiobj.LOG.debug(f"FETCHED PAGE: {self}")

        this_page_took = dt_sec_ago(obj=start_dt, exact=True)
        init_count = state["rows_initial_count"]
        this_count = self.asset_count_left
        prev_count = state["rows_to_fetch_total"]

        if init_count:
            if init_count != this_count:
                msg = f"Row total count changed from initial {init_count} to {this_count}"
                apiobj.LOG.warning(msg)
            if prev_count and prev_count != this_count:
                msg = f"Row total count changed from previous {prev_count} to {this_count}"
                apiobj.LOG.warning(msg)

        state["page"] = self.page
        state["fetch_seconds_this_page"] = this_page_took
        state["fetch_seconds_total"] += this_page_took
        state["rows_to_fetch_total"] = this_count
        state["rows_fetched_this_page"] = self.asset_count_page
        state["rows_fetched_total"] += self.asset_count_page
        state["rows_to_fetch_left"] = this_count - state["rows_fetched_total"]
        state["rows_offset"] += self.asset_count_page
        state["pages_to_fetch_total"] = self.pages_total
        state["pages_to_fetch_left"] = self.pages_left
        state["page_cursor"] = self.cursor
        state["page_number"] = self.page_number

        if not self.assets:
            state = self.process_stop(state=state, reason="no more rows returned", apiobj=apiobj)

        apiobj.LOG.debug(f"CURRENT PAGING STATE: {json_dump(state)}")
        return state

    def process_row(self, state: dict, apiobj) -> dict:
        """Pass."""
        if state["max_rows"] and state["rows_processed_total"] >= state["max_rows"]:
            state = self.process_stop(
                state=state, reason="'rows_processed_total' greater than 'max_rows'", apiobj=apiobj
            )

        return state

    def process_loop(self, state: dict, apiobj) -> dict:
        """Pass."""
        if state["max_pages"] and state["page_number"] >= state["max_pages"]:
            state = self.process_stop(
                state=state, reason="'page_number' greater than 'max_pages'", apiobj=apiobj
            )
        state["page_loop"] += 1
        return state

    def process_stop(self, state: dict, reason: str, apiobj):
        """Pass."""
        if state["stop_msg"]:
            reason = f"{state['stop_msg']} and {reason}"

        state["stop_msg"] = reason
        state["stop_fetch"] = True
        apiobj.LOG.info(f"Issuing stop of fetch due to {reason}")
        raise StopFetch(reason=reason, state=state)


@dataclasses.dataclass
class AssetById(BaseModel):
    """Pass."""

    asset: dict
    id: str

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None

    @classmethod
    def load_response(cls, data: dict, http: Http, api_endpoint, **kwargs):
        """Pass."""
        cls._check_version(data=data, api_endpoint=api_endpoint)

        sub_data = data["data"]
        asset = sub_data["attributes"]
        asset_id = sub_data["id"]
        new_data = {"asset": asset, "id": asset_id}

        schema = cls.schema()
        return cls._load_schema(schema=schema, data=new_data, http=http, api_endpoint=api_endpoint)


class CountRequestSchema(BaseSchemaJson):
    """Pass."""

    use_cache_entry = SchemaBool(missing=False)
    history = marshmallow_jsonapi.fields.Str(missing=None, allow_none=True)
    filter = marshmallow_jsonapi.fields.Str(default="", missing="", allow_none=True)

    class Meta:
        """Pass."""

        type_ = "entities_count_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return CountRequest

    @marshmallow.post_dump
    def post_dump_process(self, data, **kwargs) -> dict:
        """Pass."""
        data = {k: v for k, v in data.items() if v is not None}
        return data


@dataclasses.dataclass
class CountRequest(BaseModel, AssetMixins):
    """Pass."""

    use_cache_entry: bool = False
    history: Optional[str] = None
    filter: Optional[str] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return CountRequestSchema


@dataclasses.dataclass
class Count(BaseModel):
    """Pass."""

    value: Optional[int] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None

    @classmethod
    def load_response(cls, data: dict, http: Http, api_endpoint, **kwargs):
        """Pass."""
        cls._check_version(data=data, api_endpoint=api_endpoint)

        data_sub = data.get("data") or {}
        data_attrs = data_sub.get("attributes") or {}
        value = data_attrs.get("value")
        new_data = {"value": value}

        schema = cls.schema()
        return cls._load_schema(schema=schema, data=new_data, http=http, api_endpoint=api_endpoint)


@dataclasses.dataclass
class DestroyRequest(BaseModel):
    """Pass."""

    destroy: bool = False
    history: bool = False

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None
