# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow_jsonapi

from ...tools import calc_gb, calc_percent, json_load
from .base import BaseModel, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm


class InstanceSchema(BaseSchemaJson):
    """Pass."""

    cpu_core_threads = marshmallow_jsonapi.fields.Int(allow_none=True)
    cpu_logical_cores = marshmallow_jsonapi.fields.Int(allow_none=True)
    cpu_cores = marshmallow_jsonapi.fields.Int(allow_none=True)
    cpu_usage = marshmallow_jsonapi.fields.Int(allow_none=True)
    data_disk_free_space = marshmallow_jsonapi.fields.Number(allow_none=True)
    data_disk_size = marshmallow_jsonapi.fields.Number(allow_none=True)
    hostname = marshmallow_jsonapi.fields.Str()
    ips = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    is_master = SchemaBool()
    last_seen = SchemaDatetime(allow_none=True)
    last_snapshot_size = marshmallow_jsonapi.fields.Number(allow_none=True)
    last_updated = SchemaDatetime(allow_none=True)
    max_snapshots = marshmallow_jsonapi.fields.Int(allow_none=True)
    memory_free_space = marshmallow_jsonapi.fields.Number(allow_none=True)
    memory_size = marshmallow_jsonapi.fields.Number(allow_none=True)
    node_id = marshmallow_jsonapi.fields.Str()
    node_name = marshmallow_jsonapi.fields.Str()
    node_user_password = marshmallow_jsonapi.fields.Str()
    os_disk_free_space = marshmallow_jsonapi.fields.Number(allow_none=True)
    os_disk_size = marshmallow_jsonapi.fields.Number(allow_none=True)
    physical_cpu = marshmallow_jsonapi.fields.Int(allow_none=True)
    status = marshmallow_jsonapi.fields.Str()
    swap_cache_size = marshmallow_jsonapi.fields.Number(allow_none=True)
    swap_free_space = marshmallow_jsonapi.fields.Number(allow_none=True)
    swap_size = marshmallow_jsonapi.fields.Number(allow_none=True)
    tags = marshmallow_jsonapi.fields.Dict()
    use_as_environment_name = SchemaBool()
    remaining_snapshots_days = marshmallow_jsonapi.fields.Int(allow_none=True)
    indication_color = marshmallow_jsonapi.fields.Str(allow_none=True)
    installed_version = marshmallow_jsonapi.fields.Str(allow_none=True)

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return Instance

    class Meta:
        """Pass."""

        type_ = "instances_schema"


@dataclasses.dataclass
class Instance(BaseModel):
    """Pass."""

    hostname: str
    node_id: str
    node_name: str
    node_user_password: str
    status: str
    is_master: bool = get_field_dc_mm(mm_field=SchemaBool())
    use_as_environment_name: bool = get_field_dc_mm(mm_field=SchemaBool())
    ips: t.List[str] = dataclasses.field(default_factory=list)
    remaining_snapshots_days: t.Optional[int] = None
    cpu_core_threads: t.Optional[int] = None
    cpu_logical_cores: t.Optional[int] = None
    cpu_cores: t.Optional[int] = None
    cpu_usage: t.Optional[int] = None
    data_disk_free_space: t.Optional[float] = None
    data_disk_size: t.Optional[float] = None
    last_snapshot_size: t.Optional[float] = None
    max_snapshots: t.Optional[int] = None
    memory_free_space: t.Optional[float] = None
    memory_size: t.Optional[float] = None
    os_disk_free_space: t.Optional[float] = None
    os_disk_size: t.Optional[float] = None
    physical_cpu: t.Optional[int] = None
    swap_cache_size: t.Optional[float] = None
    swap_free_space: t.Optional[float] = None
    swap_size: t.Optional[float] = None
    last_seen: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    last_updated: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    tags: dict = dataclasses.field(default_factory=dict)
    indication_color: t.Optional[str] = None
    installed_version: t.Optional[str] = None

    id: t.Optional[str] = None
    document_meta: dict = dataclasses.field(default_factory=dict)

    name: str = dataclasses.field(init=False)
    data_disk_size_gb: float = dataclasses.field(init=False)
    data_disk_free_space_gb: float = dataclasses.field(init=False)
    data_disk_free_space_percent: float = dataclasses.field(init=False)
    memory_size_gb: float = dataclasses.field(init=False)
    memory_free_space_gb: float = dataclasses.field(init=False)
    memory_free_space_percent: float = dataclasses.field(init=False)
    swap_size_gb: float = dataclasses.field(init=False)
    swap_free_space_gb: float = dataclasses.field(init=False)
    swap_free_space_percent: float = dataclasses.field(init=False)
    os_disk_size_gb: float = dataclasses.field(init=False)
    os_disk_free_space_gb: float = dataclasses.field(init=False)
    os_disk_free_space_percent: float = dataclasses.field(init=False)

    def __post_init__(self):
        """Pass."""
        self.name = self.node_name

        self.data_disk_size_gb = calc_gb(self.data_disk_size or 0)
        self.data_disk_free_space_gb = calc_gb(self.data_disk_free_space or 0)
        self.data_disk_free_space_percent = calc_percent(
            whole=self.data_disk_size_gb, part=self.data_disk_free_space_gb
        )

        self.memory_size_gb = calc_gb(self.memory_size or 0)
        self.memory_free_space_gb = calc_gb(self.memory_free_space or 0)
        self.memory_free_space_percent = calc_percent(
            whole=self.memory_size_gb, part=self.memory_free_space_gb
        )

        self.swap_size_gb = calc_gb(self.swap_size or 0)
        self.swap_free_space_gb = calc_gb(self.swap_free_space or 0)
        self.swap_free_space_percent = calc_percent(
            whole=self.swap_size_gb, part=self.swap_free_space_gb
        )

        self.os_disk_size_gb = calc_gb(self.os_disk_size or 0)
        self.os_disk_free_space_gb = calc_gb(self.os_disk_free_space or 0)
        self.os_disk_free_space_percent = calc_percent(
            whole=self.os_disk_size_gb, part=self.os_disk_free_space_gb
        )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return InstanceSchema


@dataclasses.dataclass
class InstanceDeleteRequest(BaseModel):
    """Pass."""

    nodeIds: t.List[str]

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


@dataclasses.dataclass
class InstanceUpdateActiveRequest(BaseModel):
    """Pass."""

    nodeIds: str
    status: bool

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


@dataclasses.dataclass
class InstanceUpdateAttributesRequest(BaseModel):
    """Pass."""

    nodeIds: str
    node_name: str
    hostname: str
    use_as_environment_name: bool

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


class FactoryResetRequestSchema(BaseSchemaJson):
    """Pass."""

    approve_not_recoverable_action = SchemaBool(
        required=False, load_default=False, dump_default=False
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return FactoryResetRequest

    class Meta:
        """Pass."""

        type_ = "factory_reset_request_schema"


@dataclasses.dataclass
class FactoryResetRequest(BaseModel):
    """Pass."""

    approve_not_recoverable_action: bool = False

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return FactoryResetRequestSchema


class FactoryResetSchema(BaseSchemaJson):
    """Pass."""

    triggered = SchemaBool(required=False, load_default=False, dump_default=False)
    msg = marshmallow_jsonapi.fields.Str()

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return FactoryReset

    class Meta:
        """Pass."""

        type_ = "factory_reset_schema"


@dataclasses.dataclass
class FactoryReset(BaseModel):
    """Pass."""

    triggered: bool = False
    msg: str = ""
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return FactoryResetSchema

    def __str__(self) -> str:  # pragma: no cover
        """Pass."""
        msg = self.msg or "none"
        return f"Factory reset triggered: {self.triggered}, message: {msg}"


@dataclasses.dataclass
class Tunnel(BaseModel):
    """Pass."""

    tunnel_id: str
    tunnel_name: str
    status: str
    external_addr: str = ""
    internal_addr: str = ""
    default: bool = False
    tunnel_proxy_settings: dict = dataclasses.field(default_factory=dict)
    tunnel_email_recipients: t.List[str] = dataclasses.field(default_factory=list)
    first_seen: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    last_seen: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def _str_properties() -> t.List[str]:
        """Pass."""
        return [
            "id",
            "name",
            "status",
            "internal_addr",
            "external_addr",
            "default",
            "first_seen",
            "last_seen",
        ]

    @staticmethod
    def _str_join() -> str:  # pragma: no cover
        """Pass."""
        return ", "

    def __repr__(self):
        """Pass."""
        return self.__str__()

    @classmethod
    def load_response(cls, data: str, **kwargs) -> t.Union[str, "Tunnel"]:
        """Pass."""
        data: t.Union[str, t.List[dict]] = json_load(obj=data, error=False)
        if isinstance(data, (list, tuple)):
            return super().load_response(data=data, **kwargs)
        return data

    def to_tablize(self) -> dict:
        """Pass."""
        addresses = [
            f"Internal: {self.internal_addr}",
            f"External: {self.external_addr}",
        ]
        proxy = [
            f"Enabled: {self.proxy_enabled}",
            f"Address: {self.proxy_addr}",
            f"Port: {self.proxy_port}",
        ]
        status = [
            f"Is Default: {self.default}",
            f"Is Connected: {self.is_connected}",
            f"Status: {self.status}",
            f"First Seen: {self.first_seen}",
            f"Last Seen: {self.last_seen}",
        ]
        return {
            "Name": self.name,
            "ID": self.id,
            "Status": "\n".join(status),
            "Addresses": "\n".join(addresses),
            "Proxy": "\n".join(proxy),
        }

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None

    @property
    def is_connected(self) -> bool:
        """Pass."""
        return self.status == "connected"

    @property
    def id(self) -> str:
        """Pass."""
        return self.tunnel_id

    @property
    def name(self) -> str:
        """Pass."""
        return self.tunnel_name

    @property
    def proxy_enabled(self) -> bool:
        """Pass."""
        return self.tunnel_proxy_settings.get("enabled", False)

    @property
    def proxy_addr(self) -> str:
        """Pass."""
        return self.tunnel_proxy_settings.get("tunnel_proxy_addr", "")

    @property
    def proxy_port(self) -> str:
        """Pass."""
        return self.tunnel_proxy_settings.get("tunnel_proxy_port", "")

    @property
    def proxy_user(self) -> str:
        """Pass."""
        return self.tunnel_proxy_settings.get("tunnel_proxy_user", "")

    @property
    def proxy_password(self) -> str:
        """Pass."""
        return self.tunnel_proxy_settings.get("tunnel_proxy_password", "")
