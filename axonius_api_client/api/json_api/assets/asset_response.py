# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import logging
import typing as t

from ....constants.api import MAX_PAGE_SIZE, PAGE_SIZE
from ....exceptions import StopFetch
from ....tools import dt_now, dt_sec_ago, json_dump, parse_int_min_max
from ..base import BaseModel

LOGGER = logging.getLogger(__name__)


""" TBD: This is the marshmallow schema from axonius. It is not yet implemented.

class EntitiesSchema(BaseSchema):
    internal_axon_id = fields.Str(description='Axonius unique identifier for the asset')
    internal_axon_id_details = fields.List(fields.Str())
    adapters = fields.List(fields.Str(), description='List of adapter names composing the asset')
    adapter_details = fields.List(fields.Str())
    adapter_list_length = Integer()
    adapter_list_length_details = fields.List(fields.Str())
    adapters_data = fields.List(fields.Str())
    adapters_data_details = fields.List(fields.Str())
    unique_adapter_names = fields.List(fields.Str())
    unique_adapter_names_details = fields.List(fields.Str())
    labels = fields.List(fields.Str())
    document_meta = fields.DocumentMeta()
    
    # generate_entities_schema adds more fields based on asset type and things
    def generate_entities_schema(
        self, entity_type, entity_fields, complex_fields_preview_limit=False,
        max_field_items=False):
        new_fields = {}
        if entity_type == EntityType.Software:
            new_fields['_id'] = fields.Str(description='Unique Software CPE')
        if complex_fields_preview_limit:
            new_fields['complex_correlation_meta'] = fields.Dict()
            new_fields['complex_correlation_meta_details'] = fields.Dict()
        if max_field_items:
            new_fields['regular_correlation_meta'] = fields.Dict()
            new_fields['regular_correlation_meta_details'] = fields.Dict()
        for field in entity_fields:
            new_fields[field['name']] = self.get_field_type(field)
            new_fields[f'{field["name"]}_details'] = self.get_field_type(field)
        return type(f'{entity_type}Schema', (EntitiesSchema,), new_fields)

    def get_attribute(self, obj: typing.Any, attr: str, default: typing.Any):
        return obj.get(attr, default)

    class Meta:
        type_ = 'entities_schema'
"""


# noinspection PyUnusedLocal,PyAttributeOutsideInit
@dataclasses.dataclass
class AssetsPage(BaseModel):
    """Model for a page of assets."""

    assets: t.Optional[t.List[dict]] = dataclasses.field(default_factory=list)
    meta: t.Optional[dict] = dataclasses.field(default_factory=dict)
    empty_response: bool = False
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Dataclasses post init."""
        self.page_start_dt = dt_now()
        self.row_start_dt = dt_now()

    @classmethod
    def load_response(cls, data: dict, **kwargs) -> "AssetsPage":
        """Serialize the data into the model.

        Notes:
            This is a custom method for this model because we do not want to break
            the interface that most users expect from this model.

        """
        inner_data: t.Optional[dict] = data.get("data")
        empty: bool = inner_data is None
        assets: t.Optional[t.List[dict]] = None
        if isinstance(inner_data, list):
            assets: t.List[dict] = [
                x["attributes"]
                for x in inner_data
                if isinstance(x, dict) and isinstance(x.get("attributes"), dict)
            ]
        meta: t.Optional[dict] = data.get("meta")
        new_data = {"assets": assets, "meta": meta, "empty_response": empty}
        obj = cls(**new_data)
        cls._post_load_attrs(data=obj, **kwargs)
        return obj

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
    def page_attrs(self) -> t.List[str]:
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
        """The cursor ID for this fetch, returned from the first response when use_cursor=True."""
        return self.meta.get("cursor") or ""

    @property
    def page(self) -> dict:
        """Page metadata, returned when get_metadata=True."""
        return self.meta.get("page") or {}

    @property
    def page_number(self) -> int:
        """Current page number from the page metadata."""
        return self.page.get("number")

    @property
    def page_size(self) -> int:
        """Page size from the page metadata."""
        return self.page.get("size")

    @property
    def pages_total(self) -> int:
        """Total page count from the page metadata."""
        return self.page.get("totalPages")

    @property
    def pages_left(self) -> int:
        """Calculate the number of pages left."""
        return (self.pages_total or 0) - (self.page_number or 0)

    @property
    def asset_count_left(self) -> int:
        """Calculate the number of assets left.
        TBD: This is not correct, it should be the total minus the current fetched.
        """
        return self.asset_count_total

    @property
    def asset_count_total(self) -> int:
        """Total asset count from the page metadata."""
        return self.page.get("totalResources")

    @property
    def asset_count_page(self) -> int:
        """Count of assets returned on this page."""
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

    @staticmethod
    def process_stop(state: dict, reason: str, apiobj):
        """Pass."""
        reason = f"{state['stop_msg']} and {reason}" if state["stop_msg"] else reason
        state["stop_msg"] = reason
        state["stop_fetch"] = True
        apiobj.LOG.info(f"Issuing stop of fetch due to {reason}")
        raise StopFetch(reason=reason, state=state)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None
