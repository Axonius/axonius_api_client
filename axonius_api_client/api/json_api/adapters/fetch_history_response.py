# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import textwrap
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, SchemaDatetime, field_from_mm


class AdapterFetchHistorySchema(BaseSchemaJson):
    """Schema for response from requesting fetch history."""

    adapter = mm_fields.Dict(
        description="The internal adapter name and its display name",
        allow_none=False,
    )
    adapter_discovery_id = mm_fields.Str(
        description="The unique id of the adapter fetch record",
        allow_none=False,
    )
    client = mm_fields.Str(
        description="The connection label of the adapter connection",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    client_id = mm_fields.Str(
        description="The connection id of the adapter connection",
        allow_none=False,
    )
    devices_count = mm_fields.Integer(
        description="The amount of devices fetched by the connection",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    users_count = mm_fields.Integer(
        description="The amount of users fetched by the connection",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    resources_count = mm_fields.Integer(
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
    duration = mm_fields.Str(
        description="The duration of the fetch",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    error = mm_fields.Str(
        description="The error that the adapter raised, if any occurred",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    fetch_events_count = mm_fields.Dict(
        description="A count for each type of event - Info, Warning and Error",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    ignored_devices_count = mm_fields.Integer(
        description="The amount of devices that were ignored",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    ignored_users_count = mm_fields.Integer(
        description="The amount of users that were ignored",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    instance = mm_fields.Str(
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
    status = mm_fields.Str(
        description="The status of the fetch",
    )
    discovery_id = mm_fields.Str(
        description="The ID of the discovery cycle that originated the adapter fetch record",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    axonius_version = mm_fields.Str(
        description="The installed version of Axonius system at the time the fetch was initiated",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )
    has_configuration_changed = SchemaBool(
        description="Shows if the configuration changed since last fetch",
        load_default=False,
        dump_default=False,
    )
    last_fetch_time = SchemaDatetime(
        description="The last fetch time",
        allow_none=True,
        load_default=None,
        dump_default=None,
    )

    class Meta:
        """JSONAPI config."""

        type_ = "history_response_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return AdapterFetchHistory

    @classmethod
    def validate_attr_excludes(cls) -> t.List[str]:
        """Pass."""
        return ["document_meta", "id"]


SCHEMA = AdapterFetchHistorySchema()


@dataclasses.dataclass
class AdapterFetchHistory(BaseModel):
    """Model for response from requesting fetch history."""

    adapter: dict = field_from_mm(SCHEMA, "adapter")
    adapter_discovery_id: str = field_from_mm(SCHEMA, "adapter_discovery_id")
    client_id: str = field_from_mm(SCHEMA, "client_id")
    start_time: datetime.datetime = field_from_mm(SCHEMA, "start_time")
    status: str = field_from_mm(SCHEMA, "status")
    discovery_id: t.Optional[str] = field_from_mm(SCHEMA, "discovery_id")
    axonius_version: t.Optional[str] = field_from_mm(SCHEMA, "axonius_version")
    instance: t.Optional[str] = field_from_mm(SCHEMA, "instance")
    client: t.Optional[str] = field_from_mm(SCHEMA, "client")
    devices_count: t.Optional[int] = field_from_mm(SCHEMA, "devices_count")
    users_count: t.Optional[int] = field_from_mm(SCHEMA, "users_count")
    resources_count: t.Optional[int] = field_from_mm(SCHEMA, "resources_count")
    end_time: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "end_time")
    duration: t.Optional[str] = field_from_mm(SCHEMA, "duration")
    error: t.Optional[str] = field_from_mm(SCHEMA, "error")
    fetch_events_count: t.Optional[int] = field_from_mm(SCHEMA, "fetch_events_count")
    ignored_devices_count: t.Optional[int] = field_from_mm(SCHEMA, "ignored_devices_count")
    ignored_users_count: t.Optional[int] = field_from_mm(SCHEMA, "ignored_users_count")
    realtime: bool = field_from_mm(SCHEMA, "realtime")
    has_configuration_changed: bool = field_from_mm(SCHEMA, "has_configuration_changed")
    last_fetch_time: t.Optional[datetime.datetime] = field_from_mm(SCHEMA, "last_fetch_time")

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
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

    def __str__(self) -> str:
        """Pass."""

        def getval(prop: str) -> str:
            """Pass."""
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

        def getval(prop: str, width: t.Optional[int] = 30) -> str:
            """Pass."""
            value = getattr(self, prop, None)
            if not isinstance(value, str):
                value = "" if value is None else str(value)
            if isinstance(width, int) and len(value) > width:
                value = textwrap.fill(value, width=width)
            prop = prop.replace("_", " ").title()
            return f"{prop}: {value}"

        def getvals(props: t.List[str], width: t.Optional[int] = 30) -> str:
            """Pass."""
            return "\n".join([getval(prop=p, width=width) for p in props])

        return {
            "Details": getvals(self._props_details()),
            "Timings": getvals(self._props_timings(), width=None),
            "Results": getvals(self._props_counts() + self._props_results()),
        }

    @classmethod
    def _props_csv(cls) -> t.List[str]:
        """Pass."""
        return cls._props_custom() + [
            x for x in cls._get_field_names() if x not in cls._props_skip()
        ]

    @classmethod
    def _props_details(cls) -> t.List[str]:
        """Pass."""
        return cls._props_custom() + [
            x for x in cls._get_field_names() if x not in cls._props_details_excludes()
        ]

    @classmethod
    def _props_details_excludes(cls) -> t.List[str]:
        """Pass."""
        return (
            cls._props_custom()
            + cls._props_skip()
            + cls._props_timings()
            + cls._props_results()
            + cls._props_counts()
        )

    @classmethod
    def _props_results(cls) -> t.List[str]:
        """Pass."""
        return ["status", "error"]

    @classmethod
    def _props_counts(cls) -> t.List[str]:
        """Pass."""
        return [x for x in cls._get_field_names() if x.endswith("_count")]

    @classmethod
    def _props_timings(cls) -> t.List[str]:
        """Pass."""
        return ["start_time", "end_time", "duration"]

    @classmethod
    def _props_skip(cls) -> t.List[str]:
        """Pass."""
        return ["adapter", "document_meta"]

    @classmethod
    def _props_custom(cls) -> t.List[str]:
        """Pass."""
        return ["adapter_name", "adapter_title"]
