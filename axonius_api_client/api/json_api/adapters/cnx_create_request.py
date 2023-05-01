# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaBool, field_from_mm


# noinspection PyUnusedLocal
class CnxCreateRequestSchema(BaseSchemaJson):
    """Schema for request to create a connection."""

    connection = mm_fields.Dict(
        required=True,
        description="Connection settings",
    )
    instance_name = mm_fields.Str(
        required=True,
        description="Name of instance to add connection to",
    )
    # PBUG: why is this even a thing? can we not rely on instance id in 'instance'?
    instance = mm_fields.Str(
        required=True,
        description="ID of instance to add connection to",
    )
    connection_label = mm_fields.Str(
        load_default="",
        dump_default="",
        allow_none=True,
        description="Label for this connection",
    )
    active = SchemaBool(
        load_default=True,
        dump_default=True,
        description="Set as active or inactive",
    )
    save_and_fetch = SchemaBool(
        load_default=True,
        dump_default=True,
        description="Fetch after saving",
    )
    connection_discovery = mm_fields.Dict(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Discovery settings for this connection",
    )
    is_instances_mode = SchemaBool(
        load_default=False,
        dump_default=False,
        description="Is instance_id referring to the core instance or a collector instance",
    )
    # PBUG: why is this even a thing? can we not rely on instance id in 'instance'?
    tunnel_id = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Tunnel ID",
    )

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return CnxCreateRequest

    class Meta:
        """JSONAPI config."""

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


SCHEMA = CnxCreateRequestSchema()


@dataclasses.dataclass
class CnxCreateRequest(BaseModel):
    """Model for request to create a connection."""

    connection: dict = field_from_mm(SCHEMA, "connection")
    instance: str = field_from_mm(SCHEMA, "instance")
    instance_name: str = field_from_mm(SCHEMA, "instance_name")
    connection_label: t.Optional[str] = field_from_mm(SCHEMA, "connection_label")
    active: bool = field_from_mm(SCHEMA, "active")
    connection_discovery: t.Optional[dict] = field_from_mm(SCHEMA, "connection_discovery")
    save_and_fetch: bool = field_from_mm(SCHEMA, "save_and_fetch")
    is_instances_mode: bool = field_from_mm(SCHEMA, "is_instances_mode")
    tunnel_id: t.Optional[str] = field_from_mm(SCHEMA, "tunnel_id")

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return CnxCreateRequestSchema

    def __post_init__(self):
        """Pass."""
        self.connection_discovery = self.connection_discovery or {"enabled": False}
