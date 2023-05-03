# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow

from ....constants.adapters import DISCOVERY_NAME, GENERIC_NAME, INGESTION_NAME
from ....parsers.config import parse_schema
from ..base import BaseModel
from ..custom_fields import SchemaDatetime, dump_date, get_field_dc_mm
from .adapters_list_response import AdaptersList
from .clients_count import AdapterClientsCount


@dataclasses.dataclass
class AdapterNode(BaseModel):
    """Human friendly container for an adapter for a specific instance."""

    node_id: str
    node_name: str
    plugin_name: str
    status: str
    unique_plugin_name: str
    clients: t.Optional[t.List[dict]] = dataclasses.field(default_factory=list)
    clients_count: t.Optional[AdapterClientsCount] = None
    supported_features: t.List[str] = dataclasses.field(default_factory=list)
    is_master: bool = False

    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    _title: t.ClassVar[t.Optional[str]] = None
    _cnxs: t.ClassVar[t.Optional[t.List["AdapterNodeCnx"]]] = None
    Adapter: t.ClassVar[t.Any] = None

    def __post_init__(self):
        """Pass."""
        self.adapter_name_raw = self.plugin_name
        self.adapter_name = self._get_aname(self.plugin_name)

    @property
    def cnxs(self):
        """Pass."""

        # noinspection PyUnresolvedReferences
        def load(data):
            """Pass."""
            extra_attributes = {k: data.pop(k) for k in list(data) if k not in fields_known}
            loaded = schema.load(data, unknown=marshmallow.INCLUDE)
            loaded.AdapterNode = self
            loaded.HTTP = self.HTTP
            loaded.extra_attributes = extra_attributes
            return loaded

        if not isinstance(self._cnxs, list):
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
    def _str_properties() -> t.List[str]:
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

    @property
    def adapter_title(self) -> t.Optional[str]:
        """Pass."""
        if not hasattr(self, "_title"):
            # noinspection PyUnresolvedReferences
            basic: AdaptersList = self.HTTP.CLIENT.adapters.get_basic_cached()
            self._title: t.Optional[str] = basic.get_title(value=self.adapter_name, error=False)
        return self._title

    def to_dict_old(self) -> dict:
        """Pass."""
        ret = {
            "name": self.adapter_name,
            "name_raw": self.adapter_name_raw,
            "name_plugin": self.unique_plugin_name,
            "title": self.adapter_title,
            "node_name": self.node_name,
            "node_id": self.node_id,
            "status": self.status,
            "schemas": {
                "generic_name": self.schema_name_generic,
                "specific_name": self.schema_name_specific,
                "discovery_name": self.schema_name_discovery,
                "generic": self.schema_generic,
                "specific": self.schema_specific,
                "discovery": self.schema_discovery,
                "cnx": self.schema_cnx,
                "cnx_discovery": self.schema_cnx_discovery,
            },
            "config": {
                "generic": self.settings_generic,
                "specific": self.settings_specific,
                "discovery": self.settings_discovery,
            },
            "cnx": [x.to_dict_old() for x in self.cnxs],
            "cnx_count_total": self.clients_count.total_count,
            "cnx_count_broken": self.clients_count.error_count,
            "cnx_count_working": self.clients_count.success_count,
            "cnx_count_inactive": self.clients_count.inactive_count,
        }
        return ret

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


@dataclasses.dataclass
class AdapterNodeCnx(BaseModel):
    """Human friendly container for a connection on an adapter on an instance."""

    active: bool
    adapter_name: str
    client_id: str
    id: str
    node_id: str
    status: str
    uuid: str
    client_config: t.Optional[dict] = dataclasses.field(default_factory=dict)
    connection_advanced_config: t.Optional[dict] = dataclasses.field(default_factory=dict)
    failed_connections_attempts: t.Optional[int] = None
    failed_connections_limit_exceeded: bool = False
    connection_discovery: t.Optional[dict] = dataclasses.field(default_factory=dict)
    date_fetched: t.Optional[str] = None
    last_fetch_time: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    error: t.Optional[str] = ""
    tunnel_id: t.Optional[str] = None
    did_notify_error: t.Optional[bool] = None
    note: t.Optional[t.Any] = None

    # 2023/04/02
    last_successful_fetch: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    latest_configuration_change: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    AdapterNode: t.ClassVar[AdapterNode] = None

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
        ret = {
            "config": self.client_config,
            "config_discovery": self.connection_discovery,
            "adapter_name": self.adapter_name,
            "adapter_name_raw": self.adapter_name_raw,
            "node_name": self.node_name,
            "node_id": self.node_id,
            "status": self.status,
            "error": self.error,
            "working": self.working,
            "id": self.client_id,
            "uuid": self.uuid,
            "date_fetched": self.date_fetched,
            "last_fetch_time": dump_date(self.last_fetch_time),
        }
        return ret

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None
