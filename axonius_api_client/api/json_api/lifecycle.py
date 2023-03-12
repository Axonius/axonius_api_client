# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi

from .base import BaseModel, BaseSchemaJson


class LifecycleSchema(BaseSchemaJson):
    """Pass."""

    last_finished_time = marshmallow_jsonapi.fields.Str(allow_none=True)
    last_start_time = marshmallow_jsonapi.fields.Str(allow_none=True)
    next_run_time = marshmallow_jsonapi.fields.Number(allow_none=True)
    status = marshmallow_jsonapi.fields.Str()
    sub_phases = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())
    tunnel_status = marshmallow_jsonapi.fields.Str()

    class Meta:
        """Pass."""

        type_ = "lifecycle_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return Lifecycle


@dataclasses.dataclass
class Lifecycle(BaseModel):
    """Pass."""

    last_finished_time: t.Optional[str] = None
    last_start_time: t.Optional[str] = None
    next_run_time: t.Optional[str] = None
    status: t.Optional[str] = None
    sub_phases: t.List[dict] = dataclasses.field(default_factory=list)
    tunnel_status: t.Optional[str] = None
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return LifecycleSchema
