# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import List, Optional, Type

import marshmallow_jsonapi

from ..models import DataModel, DataSchema, DataSchemaJson
from .generic import StrValue, StrValueSchema


class ActionTypeSchema(DataSchemaJson):
    """Pass."""

    default = marshmallow_jsonapi.fields.Dict()
    schema = marshmallow_jsonapi.fields.Dict()

    class Meta:
        """Pass."""

        type_ = "actions_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return ActionType


@dataclasses.dataclass
class ActionType(DataModel):
    """Pass."""

    id: str
    default: dict
    schema: dict

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return ActionTypeSchema

    @property
    def name(self):
        """Pass."""
        return self.id

    def to_tablize(self):
        """Pass."""
        return {self._human_key(k): getattr(self, k, None) for k in self._str_properties()}

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "name",
        ]


class ActionSchema(StrValueSchema):
    """Pass."""

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return Action


class Action(StrValue):
    """Pass."""

    id: str

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return ActionSchema

    def to_tablize(self):
        """Pass."""
        return {self._human_key(k): getattr(self, k, None) for k in self._str_properties()}

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return [
            "name",
        ]

    @property
    def name(self) -> str:
        """Pass."""
        return self.value
