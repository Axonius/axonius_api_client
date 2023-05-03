# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow
import marshmallow_jsonapi.fields as mm_fields

from ..base import BaseModel, BaseSchemaJson
from ..custom_fields import SchemaDatetime, field_from_mm


class AssetByIdSchema(BaseSchemaJson):
    """Schema for getting a single assets full data."""

    internal_axon_id = mm_fields.Str(
        required=True,
        allow_none=False,
        description="Internal Axonius ID of the asset",
    )
    adapters = mm_fields.List(
        mm_fields.Dict(),
        load_default=list,
        dump_default=list,
        allow_none=True,
        description="List of adapters data for this asset",
    )
    advanced = mm_fields.List(
        mm_fields.Dict(),
        load_default=list,
        dump_default=list,
        allow_none=True,
        description="List of advanced data for this asset",
    )
    basic = mm_fields.Dict(
        load_default=dict,
        dump_default=dict,
        allow_none=True,
        description="Basic data for this asset",
    )
    aggregated_specific_data = mm_fields.Dict(
        load_default=dict,
        dump_default=dict,
        allow_none=True,
        description="Aggregated specific data for this asset",
    )
    data = mm_fields.List(
        mm_fields.Dict(),
        load_default=list,
        dump_default=list,
        allow_none=True,
        description="Data for this asset",
    )
    labels = mm_fields.List(
        mm_fields.Str(),
        load_default=list,
        dump_default=list,
        allow_none=True,
        description="Labels (tags) for this asset",
    )
    expirable_tags = mm_fields.List(
        mm_fields.Dict(),
        load_default=list,
        dump_default=list,
        allow_none=True,
        description="Expirable tags for this asset",
    )
    labels_metadata = mm_fields.List(
        mm_fields.Dict(),
        load_default=list,
        dump_default=list,
        allow_none=True,
        description="Labels (tags) metadata for this asset",
    )
    compliance_meta = mm_fields.Dict(
        load_default=dict,
        dump_default=dict,
        allow_none=True,
        description="Compliance metadata for this asset",
    )
    updated = SchemaDatetime(
        load_default=None,
        dump_default=None,
        allow_none=True,
        description="Last time this asset was updated",
    )

    class Meta:
        """Pass."""

        type_ = "entity_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return AssetById


SCHEMA = AssetByIdSchema()


@dataclasses.dataclass
class AssetById(BaseModel):
    """Model for response of getting a single assets full data."""

    id: str
    internal_axon_id: str = field_from_mm(SCHEMA, "internal_axon_id")
    adapters: t.List[dict] = field_from_mm(SCHEMA, "adapters")
    advanced: t.List[dict] = field_from_mm(SCHEMA, "advanced")
    basic: dict = field_from_mm(SCHEMA, "basic")
    aggregated_specific_data: dict = field_from_mm(SCHEMA, "aggregated_specific_data")
    data: t.List[dict] = field_from_mm(SCHEMA, "data")
    labels: t.List[str] = field_from_mm(SCHEMA, "labels")
    expirable_tags: t.List[dict] = field_from_mm(SCHEMA, "expirable_tags")
    labels_metadata: t.List[dict] = field_from_mm(SCHEMA, "labels_metadata")
    compliance_meta: dict = field_from_mm(SCHEMA, "compliance_meta")
    updated: t.Optional[str] = field_from_mm(SCHEMA, "updated")
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    SCHEMA: t.ClassVar[marshmallow.Schema] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return AssetByIdSchema


@dataclasses.dataclass
class AssetByIdOld:
    """Pass."""

    asset: t.ClassVar[dict]
    id: str

    @classmethod
    def from_new(cls, value: AssetById) -> "AssetByIdOld":
        """Pass."""
        asset: dict = value.to_dict()
        asset_id: str = value.id
        new_data = {"asset": asset, "id": asset_id}
        obj = cls(**new_data)
        return obj
