# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type, Union

import marshmallow
import marshmallow_jsonapi

from ...tools import json_load
from ..models import DataModel, DataSchema, DataSchemaJson
from .custom_fields import SchemaDatetime, get_field_dc_mm
from .generic import Deleted


class EnforcementDetailsSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    date_fetched = marshmallow_jsonapi.fields.Str()
    last_updated = SchemaDatetime(allow_none=True)
    updated_by = marshmallow_jsonapi.fields.Str(allow_none=True)
    actions_main = marshmallow_jsonapi.fields.Str()
    actions_main_type = marshmallow_jsonapi.fields.Str()
    triggers_view_name = marshmallow_jsonapi.fields.Str(allow_none=True)
    triggers_last_triggered = marshmallow_jsonapi.fields.Str(allow_none=True)
    triggers_times_triggered = marshmallow_jsonapi.fields.Int(allow_none=True)
    triggers_period = marshmallow_jsonapi.fields.Str(allow_none=True)

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementDetails

    @marshmallow.pre_load
    def pre_load_fix(self, data, **kwargs) -> Union[dict, DataModel]:
        """Pass."""
        data = {k.replace(".", "_"): v for k, v in data.items()}
        return data


@dataclasses.dataclass
class EnforcementDetails(DataModel):
    """Pass."""

    id: str
    name: str
    date_fetched: str
    updated_by: str
    actions_main_type: str
    triggers_period: Optional[str] = None
    triggers_view_name: Optional[str] = None
    last_updated: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    actions_main: str = marshmallow_jsonapi.fields.Str()
    triggers_last_triggered: Optional[str] = None
    triggers_times_triggered: Optional[int] = None
    document_meta: Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Pass."""
        self.updated_by = json_load(self.updated_by, error=False)

    @property
    def uuid(self) -> str:
        """Pass."""
        return self.id

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementDetailsSchema

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "name",
            "uuid",
            "actions_main",
            "actions_main_type",
        ]

    def to_tablize(self):
        """Pass."""
        return {self._human_key(k): getattr(self, k, None) for k in self._str_properties()}

    def get_full(self) -> "Enforcement":
        """Pass."""
        return self.CLIENT.enforcements._get_by_uuid(uuid=self.uuid)

    def delete(self) -> Deleted:
        """Pass."""
        return self.CLIENT.enforcements._delete(uuid=self.uuid)


class EnforcementSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    date_fetched = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return Enforcement


@dataclasses.dataclass
class Enforcement(DataModel):
    """Pass."""

    id: str
    uuid: str
    name: str
    date_fetched: str
    actions: dict
    triggers: List[dict]

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementSchema

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "name",
            "uuid",
        ]


class EnforcementCreateSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "enforcements_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return EnforcementCreate


@dataclasses.dataclass
class EnforcementCreate(DataModel):
    """Pass."""

    name: str
    actions: dict
    triggers: List[dict]

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return EnforcementCreateSchema


class ActionSchema(DataSchemaJson):
    """Pass."""

    default = marshmallow_jsonapi.fields.Dict()
    schema = marshmallow_jsonapi.fields.Dict()

    class Meta:
        """Pass."""

        type_ = "actions_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return Action


@dataclasses.dataclass
class Action(DataModel):
    """Pass."""

    id: str
    default: dict
    schema: dict

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return ActionSchema

    @property
    def name(self):
        """Pass."""
        return self.id
