# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type

import marshmallow_jsonapi

from ...tools import calc_gb, calc_percent
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm


class InstanceSchema(BaseSchemaJson):
    """Pass."""

    cpu_core_threads = marshmallow_jsonapi.fields.Int(allow_none=True)
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

    @staticmethod
    def get_model_cls() -> type:
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
    ips: List[str] = dataclasses.field(default_factory=list)

    cpu_core_threads: Optional[int] = None
    cpu_cores: Optional[int] = None
    cpu_usage: Optional[int] = None
    data_disk_free_space: Optional[float] = None
    data_disk_size: Optional[float] = None
    last_snapshot_size: Optional[float] = None
    max_snapshots: Optional[int] = None
    memory_free_space: Optional[float] = None
    memory_size: Optional[float] = None
    os_disk_free_space: Optional[float] = None
    os_disk_size: Optional[float] = None
    physical_cpu: Optional[int] = None
    swap_cache_size: Optional[float] = None
    swap_free_space: Optional[float] = None
    swap_size: Optional[float] = None
    last_seen: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    last_updated: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    tags: dict = dataclasses.field(default_factory=dict)

    id: Optional[str] = None
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
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return InstanceSchema


@dataclasses.dataclass
class InstanceDeleteRequest(BaseModel):
    """Pass."""

    nodeIds: List[str]


@dataclasses.dataclass
class InstanceUpdateActiveRequest(BaseModel):
    """Pass."""

    nodeIds: str
    status: bool


@dataclasses.dataclass
class InstanceUpdateAttributesRequest(BaseModel):
    """Pass."""

    nodeIds: str
    node_name: str
    hostname: str
    use_as_environment_name: bool


class FactoryResetRequestSchema(BaseSchemaJson):
    """Pass."""

    approve_not_recoverable_action = SchemaBool(required=False, missing=False)

    @staticmethod
    def get_model_cls() -> type:
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
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return FactoryResetRequestSchema


class FactoryResetSchema(BaseSchemaJson):
    """Pass."""

    triggered = SchemaBool(required=False, missing=False)
    msg = marshmallow_jsonapi.fields.Str()

    @staticmethod
    def get_model_cls() -> type:
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

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return FactoryResetSchema

    def __str__(self) -> str:
        """Pass."""
        msg = self.msg or "none"
        return f"Factory reset triggered: {self.triggered}, message: {msg}"
