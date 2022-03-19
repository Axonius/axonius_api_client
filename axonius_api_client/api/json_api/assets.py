# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import ClassVar, Dict, List, Optional, Type, Union

import marshmallow
import marshmallow_jsonapi

from ... import LOG
from ...constants.api import MAX_PAGE_SIZE, PAGE_SIZE
from ...exceptions import ApiError, StopFetch
from ...http import Http
from ...tools import coerce_int, dt_now, dt_parse, dt_sec_ago, json_dump, parse_int_min_max
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, get_field_dc_mm
from .generic import DictValue, DictValueSchema
from .resources import PaginationRequest, PaginationSchema

LOGGER = LOG.getChild("__name__")


class ModifyTagsSchema(BaseSchemaJson):
    """Pass."""

    entities = marshmallow_jsonapi.fields.Dict()
    labels = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    filter = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)

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


class HistoryDatesSchema(DictValueSchema):
    """Pass."""

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return HistoryDates


@dataclasses.dataclass
class AssetTypeHistoryDate(BaseModel):
    """Pass."""

    date_api: str
    date_api_exact: str
    asset_type: str

    @property
    def days_ago(self) -> int:
        """Pass."""
        return self.delta.days

    @property
    def delta(self) -> datetime.timedelta:
        """Pass."""
        return dt_now() - self.date

    @property
    def date(self) -> datetime.datetime:
        """Pass."""
        if not hasattr(self, "_date"):
            setattr(self, "_date", dt_parse(obj=self.date_api_exact, default_tz_utc=True))
        return getattr(self, "_date")

    def __str__(self) -> str:
        """Pass."""
        return f"date={self.date}, days_ago={self.days_ago}"

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None


@dataclasses.dataclass
class AssetTypeHistoryDates(BaseModel):
    """Pass."""

    asset_type: str
    values: dict
    DATE_ONLY_FMT: ClassVar[str] = "%Y-%m-%d"
    DATE_ONLY_VALID_FMTS: ClassVar[List[str]] = ["YYYY-MM-DD", "YYYYMMDD"]

    @property
    def dates(self) -> List[AssetTypeHistoryDate]:
        """Pass."""
        if not hasattr(self, "_dates"):
            self._dates = [
                AssetTypeHistoryDate(date_api=k, date_api_exact=v, asset_type=self.asset_type)
                for k, v in self.values.items()
            ]
        return self._dates

    @property
    def dates_by_days_ago(self) -> Dict[int, AssetTypeHistoryDate]:
        """Pass."""
        return {x.days_ago: x for x in self.dates}

    def get_date_nearest(
        self, value: Union[str, datetime.timedelta, datetime.datetime]
    ) -> AssetTypeHistoryDate:
        """Pass."""

        def get_delta(obj):
            """Pass."""
            return obj.date - pivot if obj.date >= pivot else pivot - obj.date

        pivot = dt_parse(obj=value, default_tz_utc=True)
        ret = min(self.dates, key=get_delta)
        LOGGER.info(f"Closest {self.asset_type} history date to {pivot} found: {ret}")
        return ret

    def get_date_nearest_days_ago(self, value: int) -> AssetTypeHistoryDate:
        """Pass."""

        def get_delta(obj):
            """Pass."""
            return obj.days_ago - pivot if obj.days_ago >= pivot else pivot - obj.days_ago

        pivot = coerce_int(value)
        ret = min(self.dates, key=get_delta)
        LOGGER.info(f"Closest {self.asset_type} history days ago to {pivot} found: {ret}")
        return ret

    def get_date_by_date(
        self,
        value: Optional[Union[str, datetime.timedelta, datetime.datetime]] = None,
        exact: bool = True,
    ) -> Optional[str]:
        """Pass."""
        if value:
            try:
                dt = dt_parse(obj=value, default_tz_utc=True)
            except Exception:
                valid = " or ".join(self.DATE_ONLY_VALID_FMTS)
                raise ApiError(f"Invalid history date format {value!r}, format must be {valid}")

            date_api = dt.strftime(self.DATE_ONLY_FMT)
            if date_api in self.values:
                return self.values[date_api]

            if exact:
                err = f"Invalid exact history date {date_api!r}"
                raise ApiError(f"{err}\n\n{self}\n\n{err}")
            return self.get_date_nearest(value=dt).date_api_exact

    def get_date_by_days_ago(
        self, value: Optional[Union[int, str]] = None, exact: bool = True
    ) -> Optional[str]:
        """Pass."""
        if isinstance(value, str):
            try:
                value = int(value)
            except Exception:
                raise ApiError(f"Invalid integer for exact days ago {value!r}")

        if isinstance(value, int):
            if value in self.dates_by_days_ago:
                return self.dates_by_days_ago[value].date_api_exact

            if exact and value != 0:
                nums = sorted(list(self.dates_by_days_ago))
                err = f"Invalid exact days ago {value!r} (highest={nums[-1]}, lowest={nums[0]})"
                raise ApiError(f"{err}\n{self}\n\n{err}")

            return self.get_date_nearest_days_ago(value=value).date_api_exact

    def get_date(
        self,
        date: Optional[Union[str, datetime.timedelta, datetime.datetime]] = None,
        days_ago: Optional[Union[int, str]] = None,
        exact: bool = True,
    ) -> Optional[str]:
        """Pass."""
        return self.get_date_by_date(value=date, exact=exact) or self.get_date_by_days_ago(
            value=days_ago, exact=exact
        )

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None

    def __repr__(self) -> str:
        """Pass."""
        return f"asset_type={self.asset_type}, count={len(self.dates)}"

    def __str__(self) -> str:
        """Pass."""
        items = [
            f"Valid history dates for {self.asset_type}:",
            *[f"{x}" for x in self.dates],
        ]
        return "\n".join(items)


@dataclasses.dataclass
class HistoryDates(DictValue):
    """Pass."""

    parsed: ClassVar[dict] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return HistoryDatesSchema

    def __post_init__(self):
        """Pass."""
        self.parsed = {}
        for asset_type, values in self.value.items():
            obj = AssetTypeHistoryDates(asset_type=asset_type, values=values)
            setattr(self, asset_type, obj)
            self.parsed[asset_type] = obj

    def __str__(self) -> str:
        """Pass."""
        return "\n".join([f"{x!r}" for x in self.parsed.values()])


class AssetMixins:
    """Pass."""


class AssetRequestSchema(BaseSchemaJson):
    """Pass."""

    always_cached_query = SchemaBool(load_default=False, dump_default=False)
    use_cache_entry = SchemaBool(load_default=False, dump_default=False)
    include_details = SchemaBool(load_default=False, dump_default=False)
    include_notes = SchemaBool(load_default=False, dump_default=False)
    get_metadata = SchemaBool(load_default=True, dump_default=True)
    use_cursor = SchemaBool(load_default=True, dump_default=True)

    history = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    filter = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    cursor_id = marshmallow_jsonapi.fields.Str(
        load_default=None, dump_default=None, allow_none=True
    )
    sort = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)

    excluded_adapters = marshmallow_jsonapi.fields.Dict(
        load_default={}, dump_default={}, allow_none=True
    )
    field_filters = marshmallow_jsonapi.fields.Dict(
        load_default={}, dump_default={}, allow_none=True
    )
    fields = marshmallow_jsonapi.fields.Dict(load_default={}, dump_default={}, allow_none=True)

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
class AssetRequest(AssetMixins, BaseModel):
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

    def set_page(self, limit: int = 0, offset: int = PAGE_SIZE):
        """Pass."""
        self.page = PaginationRequest(limit=limit, offset=offset)


@dataclasses.dataclass
class AssetsPage(BaseModel):
    """Pass."""

    assets: Optional[List[dict]] = dataclasses.field(default_factory=list)
    meta: Optional[dict] = dataclasses.field(default_factory=dict)
    empty_response: bool = False

    def __post_init__(self):
        """Pass."""
        self.page_start_dt = dt_now()
        self.row_start_dt = dt_now()

    @classmethod
    def load_response(cls, data: dict, http: Http, **kwargs):
        """Pass."""
        empty = data.get("data") is None
        assets = [x["attributes"] for x in data.get("data") or []]
        meta = data.get("meta") or {}
        new_data = {"assets": assets, "meta": meta, "empty_response": empty}
        schema = cls.schema()
        return cls._load_schema(schema=schema, data=new_data, http=http)

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
        max_rows = parse_int_min_max(value=max_rows, default=0, min_value=0)
        max_pages = parse_int_min_max(value=max_pages, default=0, min_value=0)
        page_start = parse_int_min_max(value=page_start, default=0, min_value=0)
        page_sleep = parse_int_min_max(value=page_sleep, default=0, min_value=0)

        row_start = parse_int_min_max(value=row_start, default=0, min_value=0)
        row_start = page_start * page_size if page_start and not row_start else row_start

        page_size = parse_int_min_max(
            value=page_size, default=PAGE_SIZE, min_value=1, max_value=MAX_PAGE_SIZE
        )
        page_size = max_rows if max_rows and max_rows < page_size else page_size

        state = {
            "fetch_seconds_this_page": 0,
            "fetch_seconds_total": 0,
            "max_pages": max_pages,
            "max_rows": max_rows,
            "page": {},
            "page_cursor": None,
            "page_loop": 1,
            "page_number": 0,
            "page_size": page_size,
            "page_sleep": page_sleep,
            "page_start": page_start,
            "pages_to_fetch_left": 0,
            "pages_to_fetch_total": 0,
            "rows_fetched_this_page": 0,
            "rows_fetched_total": 0,
            "rows_initial_count": initial_count,
            "rows_offset": row_start,
            "rows_processed_total": 0,
            "rows_to_fetch_left": 0,
            "rows_to_fetch_total": 0,
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

        if init_count and init_count != this_count:  # pragma: no cover
            apiobj.LOG.warning(f"Row total count changed from initial {init_count} to {this_count}")
        if prev_count and prev_count != this_count:  # pragma: no cover
            apiobj.LOG.warning(
                f"Row total count changed from previous {prev_count} to {this_count}"
            )

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

    def start_row(self, state: dict, apiobj, row: dict) -> dict:
        """Pass."""
        self.row_start_dt = dt_now()
        return state

    def process_row(self, state: dict, apiobj, row: dict) -> dict:
        """Pass."""
        if state["max_rows"] and state["rows_processed_total"] >= state["max_rows"]:
            state = self.process_stop(
                state=state, reason="'rows_processed_total' greater than 'max_rows'", apiobj=apiobj
            )
        state["process_seconds_row"] = dt_sec_ago(obj=self.row_start_dt, exact=True)
        return state

    def process_loop(self, state: dict, apiobj) -> dict:
        """Pass."""
        if state["max_pages"] and state["page_number"] >= state["max_pages"]:
            state = self.process_stop(
                state=state, reason="'page_number' greater than 'max_pages'", apiobj=apiobj
            )
        state["page_loop"] += 1
        process_page_took = dt_sec_ago(obj=self.page_start_dt, exact=True)
        apiobj.LOG.debug(f"Processing page took {process_page_took} seconds")
        return state

    def process_stop(self, state: dict, reason: str, apiobj):
        """Pass."""
        reason = f"{state['stop_msg']} and {reason}" if state["stop_msg"] else reason
        state["stop_msg"] = reason
        state["stop_fetch"] = True
        apiobj.LOG.info(f"Issuing stop of fetch due to {reason}")
        raise StopFetch(reason=reason, state=state)

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None


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
    def load_response(cls, data: dict, http: Http, **kwargs):
        """Pass."""
        sub_data = data["data"]
        asset = sub_data["attributes"]
        asset_id = sub_data["id"]
        new_data = {"asset": asset, "id": asset_id}

        schema = cls.schema()
        return cls._load_schema(schema=schema, data=new_data, http=http)


class CountRequestSchema(BaseSchemaJson):
    """Pass."""

    use_cache_entry = SchemaBool(load_default=False, dump_default=False)
    history = marshmallow_jsonapi.fields.Str(load_default=None, dump_default=None, allow_none=True)
    filter = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)

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
    def load_response(cls, data: dict, http: Http, **kwargs):
        """Pass."""
        data_sub = data.get("data") or {}
        data_attrs = data_sub.get("attributes") or {}
        value = data_attrs.get("value")
        new_data = {"value": value}

        schema = cls.schema()
        return cls._load_schema(schema=schema, data=new_data, http=http)


@dataclasses.dataclass
class DestroyRequest(BaseModel):
    """Pass."""

    destroy: bool = False
    history: bool = False

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None
