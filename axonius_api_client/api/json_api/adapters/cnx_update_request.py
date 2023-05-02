# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import field_from_mm
from .cnx_create_request import CnxCreateRequestSchema


# noinspection PyUnusedLocal
class CnxUpdateRequestSchema(CnxCreateRequestSchema):
    """Schema for request to update a connection."""

    instance_prev = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
    )
    instance_prev_name = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
    )
    # PBUG: why is this even a thing? can we not rely on instance id in 'instance_prev'?
    tunnel_id = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
    )

    class Meta:
        """JSONAPI config."""

        type_ = "create_connection_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return CnxUpdateRequest

    @marshmallow.post_load
    def post_load_instance_prev(self, data: dict, **kwargs) -> dict:
        """Pass."""
        data["instance_prev"] = data.get("instance_prev") or data["instance"]
        data["instance_prev_name"] = data.get("instance_prev_name") or data["instance_name"]
        return data

    @marshmallow.post_dump
    def post_dump_instance_prev(self, data: dict, **kwargs) -> dict:
        """Pass."""
        data["instance_prev"] = data.get("instance_prev") or data["instance"]
        data["instance_prev_name"] = data.get("instance_prev_name") or data["instance_name"]
        return data


SCHEMA = CnxUpdateRequestSchema()


@dataclasses.dataclass
class CnxUpdateRequest(BaseModel):
    """Model for request to update a connection."""

    connection: dict = field_from_mm(SCHEMA, "connection")
    instance: str = field_from_mm(SCHEMA, "instance")
    instance_name: str = field_from_mm(SCHEMA, "instance_name")
    connection_label: t.Optional[str] = field_from_mm(SCHEMA, "connection_label")
    active: bool = field_from_mm(SCHEMA, "active")
    connection_discovery: t.Optional[dict] = field_from_mm(SCHEMA, "connection_discovery")
    save_and_fetch: bool = field_from_mm(SCHEMA, "save_and_fetch")
    is_instances_mode: bool = field_from_mm(SCHEMA, "is_instances_mode")
    instance_prev: t.Optional[str] = field_from_mm(SCHEMA, "instance_prev")
    instance_prev_name: t.Optional[str] = field_from_mm(SCHEMA, "instance_prev_name")
    tunnel_id: t.Optional[str] = field_from_mm(SCHEMA, "tunnel_id")

    SCHEMA: t.ClassVar[BaseSchemaJson] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CnxUpdateRequestSchema

    def __post_init__(self):
        """Pass."""
        self.instance_prev = self.instance_prev or self.instance
        self.instance_prev_name = self.instance_prev_name or self.instance_name
