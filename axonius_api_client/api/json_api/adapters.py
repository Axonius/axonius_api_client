# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import re
import textwrap
from typing import ClassVar, List, Optional, Pattern, Tuple, Type

import marshmallow
import marshmallow_jsonapi

from ...constants.adapters import DISCOVERY_NAME, GENERIC_NAME, INGESTION_NAME
from ...constants.general import STR_RE_LISTY
from ...exceptions import ApiError, NotFoundError
from ...http import Http
from ...parsers.config import parse_schema
from ...parsers.tables import tablize
from ...tools import coerce_bool, listify, longest_str
from .base import BaseModel, BaseSchema, BaseSchemaJson

# from .count_operator import CountOperator, CountOperatorSchema
from .custom_fields import SchemaBool, SchemaDatetime, dump_date, get_field_dc_mm
from .generic import Metadata, MetadataSchema
from .resources import PaginationRequest, PaginationSchema
from .time_range import TimeRange, TimeRangeSchema, UnitTypes


class AdapterFetchHistorySchema(BaseSchemaJson):
    """Pass."""

    adapter = marshmallow.fields.Dict(
        description="The internal adapter name and its display name",
        allow_none=False,
    )
    adapter_discovery_id = marshmallow.fields.Str(
        description="The unique id of the adapter fetch record",
        allow_none=False,
    )
    client = marshmallow.fields.Str(
        description="The connection label of the adapter connection",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    client_id = marshmallow.fields.Str(
        description="The connection id of the adapter connection",
        allow_none=False,
    )
    devices_count = marshmallow.fields.Integer(
        description="The amount of devices fetched by the connection",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    users_count = marshmallow.fields.Integer(
        description="The amount of users fetched by the connection",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    resources_count = marshmallow.fields.Integer(
        description="The amount of resources fetched by the connection",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    start_time = SchemaDatetime(
        description="The start time of the fetch",
        allow_none=False,
    )
    end_time = SchemaDatetime(
        description="The end time of the fetch",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    duration = marshmallow.fields.Str(
        description="The duration of the fetch",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    error = marshmallow.fields.Str(
        description="The error that the adapter raised, if any occurred",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    fetch_events_count = marshmallow.fields.Dict(
        description="A count for each type of event - Info, Warning and Error",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    ignored_devices_count = marshmallow.fields.Integer(
        description="The amount of devices that were ignored",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    ignored_users_count = marshmallow.fields.Integer(
        description="The amount of users that were ignored",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    instance = marshmallow.fields.Str(
        description="The name of the Axonius instance of the connection",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    realtime = SchemaBool(
        description="Is the connection of a realtime adapter",
        load_default=False,
        dump_default=False,
    )
    status = marshmallow.fields.Str(
        description="The status of the fetch",
    )

    class Meta:
        """Pass."""

        type_ = "history_response_schema"

    @staticmethod
    def get_model_cls():
        """Pass."""
        return AdapterFetchHistory

    @classmethod
    def validate_attr_excludes(cls) -> List[str]:
        """Pass."""
        return ["document_meta", "id"]


@dataclasses.dataclass
class AdapterFetchHistory(BaseModel):
    """Pass."""

    adapter: dict = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["adapter"],
    )
    adapter_discovery_id: str = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["adapter_discovery_id"],
    )

    client_id: str = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["client_id"],
    )

    start_time: datetime.datetime = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["start_time"],
    )

    status: str = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["status"],
    )

    instance: Optional[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["instance"],
        default=None,
    )

    client: Optional[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["client"],
        default=None,
    )

    devices_count: Optional[int] = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["devices_count"],
        default=None,
    )

    users_count: Optional[int] = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["users_count"],
        default=None,
    )

    resources_count: Optional[int] = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["resources_count"],
        default=None,
    )

    end_time: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["end_time"],
        default=None,
    )

    duration: Optional[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["duration"],
        default=None,
    )

    error: Optional[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["error"],
        default=None,
    )

    fetch_events_count: Optional[int] = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["fetch_events_count"],
        default=None,
    )

    ignored_devices_count: Optional[int] = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["ignored_devices_count"],
        default=None,
    )

    ignored_users_count: Optional[int] = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["ignored_users_count"],
        default=None,
    )

    realtime: bool = get_field_dc_mm(
        mm_field=AdapterFetchHistorySchema._declared_fields["realtime"],
        default=False,
    )
    document_meta: Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls():
        """Pass."""
        return AdapterFetchHistorySchema

    @property
    def adapter_name(self) -> str:
        """Pass."""
        return self._get_aname(self.adapter["icon"])

    @property
    def adapter_name_raw(self) -> str:
        """Pass."""
        return self.adapter["icon"]

    @property
    def adapter_title(self) -> str:
        """Pass."""
        return self.adapter["text"]

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
        return {k: getattr(self, k, None) for k in self._props_csv()}

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

        return {
            "Details": getvals(self._props_details()),
            "Timings": getvals(self._props_timings(), None),
            "Results": getvals(self._props_counts() + self._props_results()),
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
        return cls._props_custom() + [
            x for x in cls._get_field_names() if x not in cls._props_details_excludes()
        ]

    @classmethod
    def _props_details_excludes(cls) -> List[str]:
        """Pass."""
        return (
            cls._props_custom()
            + cls._props_skip()
            + cls._props_timings()
            + cls._props_results()
            + cls._props_counts()
        )

    @classmethod
    def _props_results(cls) -> List[str]:
        """Pass."""
        return ["status", "error"]

    @classmethod
    def _props_counts(cls) -> List[str]:
        """Pass."""
        return [x for x in cls._get_field_names() if x.endswith("_count")]

    @classmethod
    def _props_timings(cls) -> List[str]:
        """Pass."""
        return ["start_time", "end_time", "duration"]

    @classmethod
    def _props_skip(cls) -> List[str]:
        """Pass."""
        return ["adapter", "document_meta"]

    @classmethod
    def _props_custom(cls) -> List[str]:
        """Pass."""
        return ["adapter_name", "adapter_title"]


class AdapterFetchHistoryRequestSchema(BaseSchemaJson):
    """Pass."""

    adapters_filter = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(),
        load_default=[],
        dump_default=[],
    )
    connection_labels_filter = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(),
        load_default=[],
        dump_default=[],
    )
    clients_filter = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(),
        load_default=[],
        dump_default=[],
    )
    statuses_filter = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(),
        load_default=[],
        dump_default=[],
    )
    instance_filter = marshmallow_jsonapi.fields.List(
        marshmallow_jsonapi.fields.Str(),
        load_default=[],
        dump_default=[],
    )
    sort = marshmallow_jsonapi.fields.Str(
        allow_none=True,
        load_default=None,
        dump_default=None,
        validate=AdapterFetchHistorySchema.validate_attr,
    )
    exclude_realtime = SchemaBool(load_default=False, dump_default=False)
    time_range = marshmallow_jsonapi.fields.Nested(TimeRangeSchema)
    page = marshmallow_jsonapi.fields.Nested(PaginationSchema)
    search = marshmallow_jsonapi.fields.Str(allow_none=True, load_default="", dump_default="")
    filter = marshmallow_jsonapi.fields.Str(allow_none=True, load_default="", dump_default="")

    # total_devices_filter = marshmallow_jsonapi.fields.Nested(CountOperatorSchema)
    # total_users_filter = marshmallow_jsonapi.fields.Nested(CountOperatorSchema)

    class Meta:
        """Pass."""

        type_ = "history_request_schema"

    @staticmethod
    def get_model_cls():
        """Pass."""
        return AdapterFetchHistoryRequest

    @marshmallow.post_dump
    def post_dump_process(self, data, **kwargs) -> dict:
        """Pass."""
        if "sort" in data and data["sort"] is None:
            data.pop("sort")
        return data

    @classmethod
    def validate_attrs(cls) -> dict:
        """Pass."""
        return AdapterFetchHistorySchema.validate_attrs()


@dataclasses.dataclass
class AdapterFetchHistoryRequest(BaseModel):
    """Pass."""

    adapters_filter: List[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryRequestSchema._declared_fields["adapters_filter"],
        default_factory=list,
    )
    clients_filter: List[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryRequestSchema._declared_fields["clients_filter"],
        default_factory=list,
    )
    connection_labels_filter: List[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryRequestSchema._declared_fields["connection_labels_filter"],
        default_factory=list,
    )
    instance_filter: List[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryRequestSchema._declared_fields["instance_filter"],
        default_factory=list,
    )
    statuses_filter: List[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryRequestSchema._declared_fields["statuses_filter"],
        default_factory=list,
    )
    exclude_realtime: bool = get_field_dc_mm(
        mm_field=AdapterFetchHistoryRequestSchema._declared_fields["exclude_realtime"],
        default=False,
    )
    page: Optional[PaginationRequest] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryRequestSchema._declared_fields["page"],
        default_factory=PaginationRequest,
    )
    time_range: Optional[TimeRange] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryRequestSchema._declared_fields["time_range"],
        default_factory=TimeRange,
    )
    sort: Optional[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryRequestSchema._declared_fields["sort"],
        default=None,
    )
    search: str = get_field_dc_mm(
        mm_field=AdapterFetchHistoryRequestSchema._declared_fields["search"],
        default="",
    )
    filter: Optional[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryRequestSchema._declared_fields["filter"],
        default=None,
    )
    # total_devices_filter: Optional[CountOperator] = get_field_dc_mm(
    #     mm_field=AdapterFetchHistoryRequestSchema._declared_fields["total_devices_filter"],
    #     default=CountOperator(),
    # )
    # total_users_filter: Optional[CountOperator] = get_field_dc_mm(
    #     mm_field=AdapterFetchHistoryRequestSchema._declared_fields["total_users_filter"],
    #     default=CountOperator(),
    # )

    def __post_init__(self):
        """Pass."""
        if self.page is None:
            self.page = PaginationRequest()

        if self.time_range is None:
            self.time_range = TimeRange()

        # if self.total_devices_filter is None:
        #     self.total_devices_filter = CountOperator()

        # if self.total_users_filter is None:
        #     self.total_users_filter = CountOperator()

    def set_sort(self, value: Optional[str] = None, descending: bool = False) -> Optional[str]:
        """Pass."""
        if isinstance(value, str) and value:
            value = AdapterFetchHistorySchema.validate_attr(value=value, exc_cls=NotFoundError)
            value = self._prepend_sort(value=value, descending=descending)
        else:
            value = None

        self.sort = value
        return value

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

    def set_filters(
        self,
        history_filters: "AdapterFetchHistoryFilters",
        value_type: str,
        value: Optional[List[str]] = None,
    ) -> List[str]:
        """Pass."""
        value = history_filters.check_value(value_type=value_type, value=value)
        setattr(self, f"{value_type}_filter", value)
        return value

    def set_exclude_realtime(self, value: bool) -> bool:
        """Pass."""
        value = coerce_bool(value)
        self.exclude_realtime = value
        return value

    def set_time_range(
        self,
        relative_unit_type: UnitTypes = UnitTypes.get_default(),
        relative_unit_count: Optional[int] = None,
        absolute_date_start: Optional[datetime.datetime] = None,
        absolute_date_end: Optional[datetime.datetime] = None,
    ) -> "TimeRange":
        """Pass."""
        value = TimeRange.build(
            relative_unit_type=relative_unit_type,
            relative_unit_count=relative_unit_count,
            absolute_date_start=absolute_date_start,
            absolute_date_end=absolute_date_end,
        )
        self.time_range = value
        return value

    @staticmethod
    def get_schema_cls():
        """Pass."""
        return AdapterFetchHistoryRequestSchema


class AdapterFetchHistoryFiltersSchema(BaseSchemaJson):
    """Pass."""

    adapters_filter = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())
    clients_filter = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    connection_labels_filter = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    instance_filter = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    statuses_filter = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return AdapterFetchHistoryFilters

    class Meta:
        """Pass."""

        type_ = "history_filters_response_schema"


@dataclasses.dataclass
class AdapterFetchHistoryFilters(BaseModel):
    """Pass."""

    adapters_filter: List[dict] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryFiltersSchema._declared_fields["adapters_filter"],
        default_factory=list,
    )
    clients_filter: List[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryFiltersSchema._declared_fields["clients_filter"],
        default_factory=list,
    )
    connection_labels_filter: List[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryFiltersSchema._declared_fields["connection_labels_filter"],
        default_factory=list,
    )
    instance_filter: List[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryFiltersSchema._declared_fields["instance_filter"],
        default_factory=list,
    )
    statuses_filter: List[str] = get_field_dc_mm(
        mm_field=AdapterFetchHistoryFiltersSchema._declared_fields["statuses_filter"],
        default_factory=list,
    )

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return AdapterFetchHistoryFiltersSchema

    def check_value(self, value_type: str, value: Optional[STR_RE_LISTY]) -> List[str]:
        """Pass."""

        def is_match(item):
            if isinstance(check, str) and item == check:
                return True
            if isinstance(check, Pattern) and check.search(item):
                return True
            return False

        def check_match(item):
            if isinstance(item, dict):
                for v in item.values():
                    if is_match(item=v):
                        return True
            elif isinstance(item, str):
                if is_match(item=item):
                    return True
            return False

        value_type = self.check_value_type(value_type=value_type)

        if isinstance(value, (list, tuple)):
            ret = []
            for x in value:
                ret += self.check_value(value_type=value_type, value=x)
            return ret
        elif isinstance(value, str):
            check = value.strip()
            if check.startswith("~"):
                check = re.compile(check[1:])
        elif isinstance(value, Pattern):
            check = value
        elif value is None:
            return []
        else:
            raise ApiError(f"Value must be {STR_RE_LISTY}, not type={type(value)}, value={value!r}")

        items = getattr(self, value_type)
        matches = []
        valids = []

        if isinstance(items, dict):
            for k, v in items.items():
                valids.append(v)
                if check_match(item=v):
                    matches.append(k)
        elif isinstance(items, list):
            for item in items:
                valids.append({f"Valid {value_type}": item})
                if check_match(item=item):
                    matches.append(item)
        else:
            raise ApiError(f"Unexpected type for {value_type} type={type(items)}, value={items!r}")

        if matches:
            return matches

        err = f"No {value_type} matching {value!r} using {check!r} found out of {len(valids)} items"
        err_table = tablize(value=valids, err=err)
        raise NotFoundError(err_table)

    def check_value_type(self, value_type: str) -> str:
        """Pass."""
        value_types = self.value_types()
        if value_type not in value_types:
            valids = ", ".join(value_types)
            raise ApiError(f"Invalid value_type {value_type!r}, valids: {valids}")
        return value_type

    @staticmethod
    def value_types() -> List[str]:
        """Pass."""
        return ["adapters", "clients", "connection_labels", "instances", "statuses"]

    @property
    def adapters(self) -> dict:
        """Pass."""
        return {
            x["id"]: {"name": self._get_aname(x["id"]), "name_raw": x["id"], "title": x["name"]}
            for x in self.adapters_filter
        }

    @property
    def clients(self) -> List[str]:
        """Pass."""
        return self.clients_filter

    @property
    def connection_labels(self) -> List[str]:
        """Pass."""
        return self.connection_labels_filter

    @property
    def instances(self) -> List[str]:
        """Pass."""
        return self.instance_filter

    @property
    def statuses(self) -> List[str]:
        """Pass."""
        return self.statuses_filter

    def __str__(self):
        """Pass."""
        items = [
            f"adapters: {len(self.adapters)}",
            f"clients: {len(self.clients)}",
            f"connection_labels: {len(self.connection_labels)}",
            f"instances: {len(self.instances)}",
            f"statuses: {len(self.statuses)}",
        ]
        return ", ".join(items)

    def __repr__(self):
        """Pass."""
        return self.__str__()


class AdapterSchema(BaseSchemaJson):
    """Pass."""

    adapters_data = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return Adapter

    class Meta:
        """Pass."""

        type_ = "adapters_schema"


class AdaptersListSchema(MetadataSchema):
    """Pass."""

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return AdaptersList


class AdaptersRequestSchema(BaseSchemaJson):
    """Pass."""

    filter = marshmallow_jsonapi.fields.Str(allow_none=True)
    get_clients = SchemaBool(load_default=False, dump_default=False)

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return AdaptersRequest

    class Meta:
        """Pass."""

        type_ = "adapters_request_schema"


class AdapterSettingsSchema(MetadataSchema):
    """Pass."""

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return AdapterSettings


class AdapterSettingsUpdateSchema(BaseSchemaJson):
    """Pass."""

    config = marshmallow_jsonapi.fields.Dict(required=True)
    configName = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    pluginId = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    prefix = marshmallow_jsonapi.fields.Str(load_default="adapters", dump_default="adapters")

    class Meta:
        """Pass."""

        type_ = "settings_schema"

    @staticmethod
    def get_model_cls() -> Optional[type]:
        """Pass."""
        return AdapterSettingsUpdate


class CnxCreateRequestSchema(BaseSchemaJson):
    """Pass."""

    connection = marshmallow_jsonapi.fields.Dict(required=True)  # config of connection
    connection_label = marshmallow_jsonapi.fields.Str(
        required=False, load_default="", dump_default="", allow_none=True
    )
    instance = marshmallow_jsonapi.fields.Str(required=True)  # instance ID
    active = SchemaBool(
        required=False, load_default=True, dump_default=True
    )  # set as active or inactive
    save_and_fetch = SchemaBool(
        required=False, load_default=True, dump_default=True
    )  # perform a fetch after saving
    connection_discovery = marshmallow_jsonapi.fields.Dict(
        required=False, load_default=None, dump_default=None, allow_none=True
    )  # connection specific discovery scheduling
    instance_name = marshmallow_jsonapi.fields.Str(required=True)
    # PBUG: why is this even a thing? can we not rely on instance id in 'instance'?
    is_instances_mode = SchemaBool(required=False, load_default=False, dump_default=False)
    # PBUG: why is this even a thing? can we not rely on instance id in 'instance'?
    tunnel_id = marshmallow_jsonapi.fields.Str(
        required=False, load_default=None, dump_default=None, allow_none=True
    )

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return CnxCreateRequest

    class Meta:
        """Pass."""

        type_ = "create_connection_schema"

    @marshmallow.post_load
    def post_load_fix_cd(self, data: dict, **kwargs) -> dict:
        """Pass."""
        data["connection_discovery"] = data.get("connection_discovery") or {"enabled": False}
        return data

    @marshmallow.post_dump
    def post_dump_fix_cd(self, data: dict, **kwargs) -> dict:
        """Pass."""
        data["connection_discovery"] = data.get("connection_discovery") or {"enabled": False}
        return data


class CnxTestRequestSchema(BaseSchemaJson):
    """Pass."""

    connection = marshmallow_jsonapi.fields.Dict(required=True)  # config of connection
    instance = marshmallow_jsonapi.fields.Str(required=True)  # instance ID
    tunnel_id = marshmallow_jsonapi.fields.Str(
        required=False, load_default=None, dump_default=None, allow_none=True
    )

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return CnxTestRequest

    class Meta:
        """Pass."""

        type_ = "test_connection_schema"


class CnxDeleteSchema(BaseSchemaJson):
    """Pass."""

    client_id = marshmallow_jsonapi.fields.Str()

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return CnxDelete

    class Meta:
        """Pass."""

        type_ = "deleted_connections_schema"


class CnxUpdateRequestSchema(CnxCreateRequestSchema):
    """Pass."""

    instance_prev = marshmallow_jsonapi.fields.Str(
        required=False, load_default=None, dump_default=None, allow_none=True
    )
    instance_prev_name = marshmallow_jsonapi.fields.Str(
        required=False, load_default=None, dump_default=None, allow_none=True
    )
    # PBUG: why is this even a thing? can we not rely on instance id in 'instance_prev'?
    tunnel_id = marshmallow_jsonapi.fields.Str(
        required=False, load_default=None, dump_default=None, allow_none=True
    )

    def __post_init__(self):
        """Pass."""

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return CnxUpdateRequest

    @marshmallow.post_load
    def post_load_iprev(self, data: dict, **kwargs) -> dict:
        """Pass."""
        data["instance_prev"] = data.get("instance_prev") or data["instance"]
        data["instance_prev_name"] = data.get("instance_prev_name") or data["instance_name"]
        return data

    @marshmallow.post_dump
    def post_dump_iprev(self, data: dict, **kwargs) -> dict:
        """Pass."""
        data["instance_prev"] = data.get("instance_prev") or data["instance"]
        data["instance_prev_name"] = data.get("instance_prev_name") or data["instance_name"]
        return data


class CnxModifyResponseSchema(BaseSchemaJson):
    """Pass."""

    active = SchemaBool()
    client_id = marshmallow_jsonapi.fields.Str()
    error = marshmallow_jsonapi.fields.Str(allow_none=True)
    status = marshmallow_jsonapi.fields.Str()
    failed_connections_limit_exceeded = marshmallow_jsonapi.fields.Int(allow_none=True)

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return CnxModifyResponse

    class Meta:
        """Pass."""

        type_ = "connections_details_schema"


class CnxDeleteRequestSchema(BaseSchemaJson):
    """Pass."""

    is_instances_mode = SchemaBool(load_default=False, dump_default=False)
    delete_entities = SchemaBool(load_default=False, dump_default=False)
    instance = marshmallow_jsonapi.fields.Str()
    instance_name = marshmallow_jsonapi.fields.Str()

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return CnxDeleteRequest

    class Meta:
        """Pass."""

        type_ = "delete_connections_schema"


class CnxLabelsSchema(MetadataSchema):
    """Pass."""

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return CnxLabels

    class Meta:
        """Pass."""

        type_ = "metadata_schema"


@dataclasses.dataclass
class AdapterClientsCount(BaseModel):
    """Pass."""

    error_count: Optional[int] = None
    inactive_count: Optional[int] = None
    success_count: Optional[int] = None
    total_count: Optional[int] = None

    def __post_init__(self):
        """Pass."""
        for count in [
            "error_count",
            "inactive_count",
            "success_count",
            "total_count",
        ]:
            value = getattr(self, count, None)
            if value is None:
                setattr(self, count, 0)

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None


@dataclasses.dataclass
class AdapterNode(BaseModel):
    """Pass."""

    node_id: str
    node_name: str
    plugin_name: str
    status: str
    unique_plugin_name: str
    clients: Optional[List[dict]] = dataclasses.field(default_factory=list)
    clients_count: Optional[AdapterClientsCount] = None
    supported_features: List[str] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        """Pass."""
        self.adapter_name_raw = self.plugin_name
        self.adapter_name = self._get_aname(self.plugin_name)

    @property
    def cnxs(self):
        """Pass."""

        def load(data):
            extra_attributes = {k: data.pop(k) for k in list(data) if k not in fields_known}
            loaded = schema.load(data, unknown=marshmallow.INCLUDE)
            loaded.AdapterNode = self
            loaded.HTTP = self.HTTP
            loaded.extra_attributes = extra_attributes
            return loaded

        if not hasattr(self, "_cnxs"):
            fields_known = [x.name for x in dataclasses.fields(AdapterNodeCnx)]
            schema = AdapterNodeCnx.schema()
            self._cnxs = [load(x) for x in self.clients]

        return self._cnxs

    @property
    def schema_name_specific(self) -> str:
        """Pass."""
        ret = ""
        skips = [self.schema_name_generic, self.schema_name_discovery, self.schema_name_ingestion]
        if self._meta:
            if self._meta:
                matches = [x for x in self._meta if x.endswith("Adapter") and x not in skips]
                if matches:
                    ret = matches[0]
        return ret

    @property
    def schema_name_ingestion(self) -> str:
        """Pass."""
        ret = INGESTION_NAME
        return ret

    @property
    def schema_name_generic(self) -> str:
        """Pass."""
        return GENERIC_NAME

    @property
    def schema_name_discovery(self) -> str:
        """Pass."""
        return DISCOVERY_NAME

    @property
    def _meta(self) -> dict:
        """Pass."""
        return self.Adapter.document_meta

    @property
    def _schema_specific(self) -> dict:
        """Pass."""
        name = self.schema_name_specific
        return self._meta["config"][name]["schema"] if self._meta and name else {}

    @property
    def _schema_generic(self) -> dict:
        """Pass."""
        name = self.schema_name_generic
        return self._meta["config"][name]["schema"] if self._meta and name else {}

    @property
    def _schema_discovery(self) -> dict:
        """Pass."""
        name = self.schema_name_discovery
        return self._meta["config"][name]["schema"] if self._meta and name else {}

    @property
    def _schema_cnx(self) -> dict:
        return self._meta["schema"] if self._meta else {}

    @property
    def _schema_cnx_discovery(self) -> dict:
        name = "connectionDiscoverySchema"
        return self._meta["clients_schema"][name] if self._meta else {}

    @property
    def schema_specific(self) -> dict:
        """Pass."""
        schema = self._schema_specific
        return parse_schema(schema) if schema else {}

    @property
    def schema_generic(self) -> dict:
        """Pass."""
        schema = self._schema_generic
        return parse_schema(schema) if schema else {}

    @property
    def schema_discovery(self) -> dict:
        """Pass."""
        schema = self._schema_discovery
        return parse_schema(schema) if schema else {}

    @property
    def schema_cnx(self) -> dict:
        """Pass."""
        schema = self._schema_cnx
        return parse_schema(schema) if schema else {}

    @property
    def schema_cnx_discovery(self) -> dict:
        """Pass."""
        schema = self._schema_cnx_discovery
        return parse_schema(schema) if schema else {}

    @property
    def settings_specific(self) -> dict:
        """Pass."""
        if self._meta and self.schema_name_specific:
            return self._meta["config"][self.schema_name_specific]["config"]
        return {}

    @property
    def settings_generic(self) -> dict:
        """Pass."""
        return self._meta["config"][self.schema_name_generic]["config"] if self._meta else {}

    @property
    def settings_discovery(self) -> dict:
        """Pass."""
        return self._meta["config"][self.schema_name_discovery]["config"] if self._meta else {}

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "adapter_name",
            "node_name",
            "node_id",
            "status",
            "clients_count",
            "supported_features",
        ]

    @staticmethod
    def _str_join() -> str:
        """Pass."""
        return ", "

    def to_dict_old(self, basic_data: Optional[List[dict]] = None) -> dict:
        """Pass."""
        basic_data = basic_data or {}
        title = basic_data.get(self.adapter_name, {}).get("title")

        ret = {}
        ret["name"] = self.adapter_name
        ret["name_raw"] = self.adapter_name_raw
        ret["name_plugin"] = self.unique_plugin_name
        ret["title"] = title
        ret["node_name"] = self.node_name
        ret["node_id"] = self.node_id
        ret["status"] = self.status
        ret["schemas"] = {
            "generic_name": self.schema_name_generic,
            "specific_name": self.schema_name_specific,
            "discovery_name": self.schema_name_discovery,
            "generic": self.schema_generic,
            "specific": self.schema_specific,
            "discovery": self.schema_discovery,
            "cnx": self.schema_cnx,
            "cnx_discovery": self.schema_cnx_discovery,
        }
        ret["config"] = {
            "generic": self.settings_generic,
            "specific": self.settings_specific,
            "discovery": self.settings_discovery,
        }
        ret["cnx"] = [x.to_dict_old() for x in self.cnxs]
        ret["cnx_count_total"] = self.clients_count.total_count
        ret["cnx_count_broken"] = self.clients_count.error_count
        ret["cnx_count_working"] = self.clients_count.success_count
        ret["cnx_count_inactive"] = self.clients_count.inactive_count
        return ret

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None


@dataclasses.dataclass
class Adapter(BaseModel):
    """Pass."""

    adapters_data: List[dict]
    id: str
    document_meta: Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Pass."""
        self.adapter_name_raw = self.id
        self.adapter_name = self._get_aname(self.id)
        self.document_meta = self.document_meta.pop(self.id, None)
        """
        document_meta: {}
            config: {} - adapter advanced settings
                ActiveDirectoryAdapter: {} - adapter specific advanced settings
                    config: {} - current config
                    schema: {} - schema for config
                AdapterBase: {} - adapter generic advanced settings
                    config: {} - current config
                    schema: {} - schema for config
                DiscoverySchema: {} - adapter discovery advanced settings
                    config: {} - current config
                    schema: {} - schema for config
            schema: {} - adapter connection schema
            clients_schema: {} - adapter connection special schemas
                settings: {} - for 'connect_via_tunnel' - will ignore for now
                connectionDiscoverySchema: {} - schema for connection specific discovery settings
        """

    @property
    def adapter_nodes(self) -> List[AdapterNode]:
        """Pass."""

        def load(data):
            extra_attributes = {k: data.pop(k) for k in list(data) if k not in fields_known}
            loaded = schema.load(data, unknown=marshmallow.INCLUDE)
            loaded.Adapter = self
            loaded.HTTP = self.HTTP
            loaded.extra_attributes = extra_attributes
            return loaded

        if not hasattr(self, "_adapter_nodes"):
            fields_known = [x.name for x in dataclasses.fields(AdapterNode)]
            schema = AdapterNode.schema()
            self._adapter_nodes = [load(x) for x in self.adapters_data]

        return self._adapter_nodes

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return AdapterSchema

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return ["adapter_name", "adapter_nodes"]


@dataclasses.dataclass
class AdapterNodeCnx(BaseModel):
    """Pass."""

    active: bool
    adapter_name: str
    client_id: str
    id: str
    node_id: str
    status: str
    uuid: str
    client_config: Optional[dict] = dataclasses.field(default_factory=dict)
    connection_advanced_config: Optional[dict] = dataclasses.field(default_factory=dict)
    failed_connections_attempts: Optional[int] = None
    failed_connections_limit_exceeded: bool = False
    connection_discovery: Optional[dict] = dataclasses.field(default_factory=dict)
    date_fetched: Optional[str] = None
    last_fetch_time: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    error: Optional[str] = ""
    tunnel_id: Optional[str] = None
    did_notify_error: Optional[bool] = None

    def __post_init__(self):
        """Pass."""
        self.adapter_name_raw = self.adapter_name
        self.adapter_name = self._get_aname(self.adapter_name)

    @property
    def working(self) -> bool:
        """Pass."""
        return self.status == "success" and not self.error

    @property
    def node_name(self) -> str:
        """Pass."""
        return self.AdapterNode.node_name

    @property
    def label(self) -> str:
        """Pass."""
        return self.client_config.get("connection_label") or ""

    @property
    def schema_cnx(self) -> dict:
        """Pass."""
        return self.AdapterNode.schema_cnx

    @property
    def schema_cnx_discovery(self) -> dict:
        """Pass."""
        return self.AdapterNode.schema_cnx_discovery

    def to_dict_old(self) -> dict:
        """Pass."""
        ret = {}
        ret["config"] = self.client_config
        ret["config_discovery"] = self.connection_discovery
        ret["adapter_name"] = self.adapter_name
        ret["adapter_name_raw"] = self.adapter_name_raw
        ret["node_name"] = self.node_name
        ret["node_id"] = self.node_id
        ret["status"] = self.status
        ret["error"] = self.error
        ret["working"] = self.working
        ret["id"] = self.client_id
        ret["uuid"] = self.uuid
        ret["date_fetched"] = self.date_fetched
        ret["last_fetch_time"] = dump_date(self.last_fetch_time)
        return ret

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None


@dataclasses.dataclass
class AdaptersRequest(BaseModel):
    """Pass."""

    filter: Optional[str] = None
    # PBUG: how is this even used?
    get_clients: bool = False

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return AdaptersRequestSchema


@dataclasses.dataclass
class AdapterSettings(Metadata):
    """Pass."""

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return AdapterSettingsSchema

    @property
    def type_map(self) -> dict:
        """Pass."""
        ret = {
            "generic": self.schema_config_generic,
            "discovery": self.schema_config_discovery,
        }
        if self.schema_config_specific:
            ret["specific"] = self.schema_config_specific
        return ret

    @property
    def schema_config_specific(self) -> dict:
        """Pass."""
        ret = {}
        if self.schema_specific:
            ret = {
                "schema": self.schema_specific,
                "config": self.config_specific,
                "config_name": self.schema_name_specific,
            }
        return ret

    @property
    def schema_config_discovery(self) -> dict:
        """Pass."""
        ret = {
            "schema": self.schema_discovery,
            "config": self.config_discovery,
            "config_name": self.schema_name_discovery,
        }
        return ret

    @property
    def schema_config_generic(self) -> dict:
        """Pass."""
        ret = {
            "schema": self.schema_generic,
            "config": self.config_generic,
            "config_name": self.schema_name_generic,
        }
        return ret

    @property
    def schema_name_specific(self) -> str:
        """Pass."""
        ret = ""
        skips = [self.schema_name_generic, self.schema_name_discovery, self.schema_name_ingestion]
        if self._meta:
            matches = [x for x in self._meta if x.endswith("Adapter") and x not in skips]
            if matches:
                ret = matches[0]
        return ret

    @property
    def schema_name_ingestion(self) -> str:
        """Pass."""
        ret = INGESTION_NAME
        return ret

    @property
    def schema_name_generic(self) -> str:
        """Pass."""
        ret = GENERIC_NAME
        return ret

    @property
    def schema_name_discovery(self) -> str:
        """Pass."""
        ret = DISCOVERY_NAME
        return ret

    @property
    def _meta(self) -> dict:
        """Pass."""
        ret = self.document_meta["advanced_settings"]
        return ret

    @property
    def _schema_specific(self) -> dict:
        """Pass."""
        ret = {}
        if self.schema_name_specific:
            ret = self._meta[self.schema_name_specific]["schema"]
        return ret

    @property
    def _schema_generic(self) -> dict:
        """Pass."""
        ret = {}
        if self.schema_name_generic:
            ret = self._meta[self.schema_name_generic]["schema"]
        return ret

    @property
    def _schema_discovery(self) -> dict:
        """Pass."""
        ret = {}
        if self.schema_name_discovery:
            ret = self._meta[self.schema_name_discovery]["schema"]
        return ret

    @property
    def schema_specific(self) -> dict:
        """Pass."""
        ret = {}
        if self._schema_specific:
            ret = parse_schema(self._schema_specific)
        return ret

    @property
    def schema_generic(self) -> dict:
        """Pass."""
        ret = {}
        if self._schema_generic:
            ret = parse_schema(self._schema_generic)
        return ret

    @property
    def schema_discovery(self) -> dict:
        """Pass."""
        ret = parse_schema(self._schema_discovery)
        return ret

    @property
    def config_specific(self) -> dict:
        """Pass."""
        ret = {}
        if self.schema_name_specific:
            ret = self._meta[self.schema_name_specific]["config"]
        return ret

    @property
    def config_generic(self) -> dict:
        """Pass."""
        ret = self._meta[self.schema_name_generic]["config"]
        return ret

    @property
    def config_discovery(self) -> dict:
        """Pass."""
        ret = self._meta[self.schema_name_discovery]["config"]
        return ret


@dataclasses.dataclass
class AdapterSettingsUpdate(BaseModel):
    """Pass."""

    config: dict
    pluginId: str
    configName: str
    prefix: str = "adapters"

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return AdapterSettingsUpdateSchema


@dataclasses.dataclass
class AdaptersList(Metadata):
    """Pass."""

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return AdaptersListSchema

    @property
    def adapters(self) -> dict:
        """Pass."""
        items = self.document_meta["adapter_list"]
        ret = {}
        for item in items:
            name_raw = item["name"]
            name = self._get_aname(name_raw)
            item["name_raw"] = name_raw
            item["name"] = name
            ret[name] = item
        return ret

    def find_by_name(self, value: str) -> dict:
        """Pass."""
        find_value = self._get_aname(value)
        adapters = self.adapters
        if find_value not in adapters:
            padding = longest_str(list(adapters))
            valid = [f"{k:{padding}}: {v['title']}" for k, v in adapters.items()]
            pre = f"No adapter found with name of {value!r}"
            msg = [pre, "", *valid, "", pre]
            raise NotFoundError("\n".join(msg))
        ret = adapters[find_value]
        return ret


@dataclasses.dataclass
class CnxCreateRequest(BaseModel):
    """Pass."""

    connection: dict
    instance: str
    instance_name: str
    connection_label: Optional[str] = None
    active: bool = True
    connection_discovery: Optional[dict] = None
    save_and_fetch: bool = True
    is_instances_mode: bool = False
    tunnel_id: Optional[str] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return CnxCreateRequestSchema

    def __post_init__(self):
        """Pass."""
        self.connection_discovery = self.connection_discovery or {"enabled": False}


@dataclasses.dataclass
class CnxTestRequest(BaseModel):
    """Pass."""

    connection: dict
    instance: str
    tunnel_id: Optional[str] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return CnxTestRequestSchema


@dataclasses.dataclass
class CnxUpdateRequest(BaseModel):
    """Pass."""

    connection: dict
    instance: str
    instance_name: str
    connection_label: Optional[str] = None
    active: bool = True
    connection_discovery: Optional[dict] = None
    save_and_fetch: bool = True
    is_instances_mode: bool = False
    instance_prev: Optional[str] = None
    instance_prev_name: Optional[str] = None
    tunnel_id: Optional[str] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return CnxUpdateRequestSchema

    def __post_init__(self):
        """Pass."""
        self.instance_prev = self.instance_prev or self.instance
        self.instance_prev_name = self.instance_prev_name or self.instance_name


@dataclasses.dataclass
class CnxModifyResponse(BaseModel):
    """Pass."""

    status: str
    client_id: str
    id: str
    active: bool = True
    error: Optional[str] = None
    failed_connections_limit_exceeded: Optional[int] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return CnxModifyResponseSchema

    @property
    def uuid(self) -> str:
        """Pass."""
        return self.id

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return ["client_id", "uuid", "status", "error"]

    @property
    def working(self) -> bool:
        """Pass."""
        return self.status == "success" and not self.error


@dataclasses.dataclass
class CnxDeleteRequest(BaseModel):
    """Pass."""

    instance: str
    instance_name: str
    is_instances_mode: bool = False
    delete_entities: bool = False

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return CnxDeleteRequestSchema


@dataclasses.dataclass
class CnxDelete(BaseModel):
    """Pass."""

    client_id: str

    def __post_init__(self):
        """Pass."""
        try:
            self.client_id = eval(self.client_id)["client_id"]
        except Exception:  # pragma: no cover
            pass

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return CnxDeleteSchema


@dataclasses.dataclass
class CnxLabels(Metadata):
    """Pass."""

    document_meta: dict

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return CnxLabelsSchema

    @property
    def labels(self) -> List[dict]:
        """Pass."""
        return self.document_meta.get("labels") or []

    @property
    def label_values(self) -> List[str]:
        """Pass."""
        return list(set([x["label"] for x in self.labels]))

    def get_label(self, cnx: "Cnx") -> str:
        """Pass."""
        aname = cnx.adapter_name_raw
        node = cnx.node_id
        cid = cnx.client_id
        labels = self.labels
        ret = ""

        for item in labels:
            ianame = item["plugin_name"]
            inode = item["node_id"]
            ilabel = item["label"]
            icid = item["client_id"]

            if all([ianame == aname, inode == node, icid == cid]):
                ret = ilabel
                break

        return ret


@dataclasses.dataclass(repr=False)
class Cnx(BaseModel):
    """Pass."""

    active: bool
    adapter_name: str
    client_id: str
    uuid: str
    node_id: str
    node_name: str
    status: str

    client_config: Optional[dict] = dataclasses.field(default_factory=dict)
    connection_discovery: Optional[dict] = dataclasses.field(default_factory=dict)
    connection_advanced_config: Optional[dict] = dataclasses.field(default_factory=dict)
    date_fetched: Optional[str] = None
    last_fetch_time: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    error: Optional[str] = ""
    tunnel_id: Optional[str] = None
    failed_connections_limit_exceeded: Optional[int] = None
    adapter_name_raw: ClassVar[str] = None
    connection_label: ClassVar[str] = None
    PARENT: ClassVar["Cnxs"] = None
    HTTP: ClassVar[Http] = None

    def __post_init__(self):
        """Pass."""
        self.adapter_name_raw = self.adapter_name
        self.adapter_name = self._get_aname(self.adapter_name)

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "adapter_name",
            "client_id",
            "uuid",
            "node_id",
            "node_name",
            "status",
            "error",
        ]

    def __repr__(self):
        """Pass."""
        return self.__str__()

    @property
    def working(self) -> bool:
        """Pass."""
        return self.status == "success" and not self.error

    def to_dict_old(self) -> dict:
        """Pass."""
        ret = {}
        ret["active"] = self.active
        ret["adapter_name"] = self.adapter_name
        ret["adapter_name_raw"] = self.adapter_name_raw
        ret["id"] = self.client_id
        ret["uuid"] = self.uuid
        ret["node_id"] = self.node_id
        ret["node_name"] = self.node_name
        ret["status"] = self.status
        ret["config"] = self.client_config
        ret["config_discovery"] = self.connection_discovery
        ret["date_fetched"] = self.date_fetched
        ret["last_fetched_time"] = dump_date(self.last_fetch_time)
        ret["working"] = self.working
        ret["error"] = self.error
        ret["tunnel_id"] = self.tunnel_id
        ret["schemas"] = self.PARENT.schema_cnx
        ret["schema_discovery"] = self.PARENT.schema_discovery
        ret["connection_label"] = self.connection_label
        return ret

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None


@dataclasses.dataclass
class Cnxs(BaseModel):
    """Pass."""

    cnxs: List[Cnx]
    meta: dict

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return None

    @classmethod
    def load_response(cls, data: dict, http: Http, **kwargs):
        """Pass."""

        def load_cnx(obj):
            data = obj.get("attributes")
            loaded = None
            if data:
                extra_attributes = {k: data.pop(k) for k in list(data) if k not in fields_known}
                loaded = schema.load(data, unknown=marshmallow.INCLUDE)
                loaded.extra_attributes = extra_attributes
            return loaded

        fields_known = [x.name for x in dataclasses.fields(Cnx)]
        schema = Cnx.schema()

        meta = data["meta"]
        cnxs_raw = listify(data["data"])
        cnxs = [y for y in [load_cnx(x) for x in cnxs_raw] if y]

        loaded = cls(cnxs=cnxs, meta=meta)
        loaded.HTTP = http
        labels = loaded.get_labels()

        for cnx in loaded.cnxs:
            cnx.PARENT = loaded
            cnx.HTTP = loaded.HTTP
            cnx.connection_label = labels.get_label(cnx=cnx)

        return loaded

    @property
    def schema_discovery(self) -> dict:
        """Pass."""
        return parse_schema(self.meta["connectionDiscoverySchema"])

    @property
    def schema_cnx(self) -> dict:
        """Pass."""
        return parse_schema(self.meta["schema"])

    '''
    def find_by_node_id(self, value: str) -> List[Cnx]:
        """Pass."""
        return [x for x in self.cnxs if x.node_id == value]
    '''

    def get_labels(self, cached: bool = False) -> List[dict]:
        """Pass."""
        from .. import ApiEndpoints

        if not cached or not getattr(self, "_get_labels", None):
            self._get_labels = ApiEndpoints.adapters.labels_get.perform_request(http=self.HTTP)

        return getattr(self, "_get_labels")
