# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import ClassVar, List, Optional, Type

import marshmallow
import marshmallow_jsonapi

from ...constants.adapters import DISCOVERY_NAME, GENERIC_NAME
from ...exceptions import NotFoundError
from ...http import Http
from ...parsers.config import parse_schema
from ...tools import listify, longest_str, strip_right
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, dump_date, get_field_dc_mm
from .generic import Metadata, MetadataSchema


def get_aname(value: str) -> str:
    """Pass."""
    return strip_right(obj=str(value or ""), fix="_adapter")


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
        self.adapter_name = get_aname(self.plugin_name)

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
        if self._meta:
            for name in self._meta["config"]:
                if name not in [self.schema_name_generic, self.schema_name_discovery]:
                    return name
        return ""

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
        self.adapter_name = get_aname(self.id)
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

    def __post_init__(self):
        """Pass."""
        self.adapter_name_raw = self.adapter_name
        self.adapter_name = get_aname(self.adapter_name)

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
        if self._meta:
            for name in self._meta:
                if name not in [self.schema_name_generic, self.schema_name_discovery]:
                    ret = name
                    break
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
        ret = {
            get_aname(x["name"]): {
                "title": x["title"],
                "name_raw": x["name"],
                "name": get_aname(x["name"]),
            }
            for x in items
        }
        return ret

    def find_by_name(self, value: str) -> dict:
        """Pass."""
        find_value = get_aname(value)
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
        self.adapter_name = get_aname(self.adapter_name)

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
