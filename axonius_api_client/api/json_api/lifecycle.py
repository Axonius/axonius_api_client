# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import List, Optional, Type

import marshmallow_jsonapi

from ..models import DataModel, DataSchema, DataSchemaJson


class LifecycleSchema(DataSchemaJson):
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
    def _get_model_cls() -> type:
        """Pass."""
        return Lifecycle


@dataclasses.dataclass
class Lifecycle(DataModel):
    """Pass."""

    last_finished_time: Optional[str] = None
    last_start_time: Optional[str] = None
    next_run_time: Optional[str] = None
    status: Optional[str] = None
    sub_phases: List[dict] = dataclasses.field(default_factory=list)
    tunnel_status: Optional[str] = None

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return LifecycleSchema
