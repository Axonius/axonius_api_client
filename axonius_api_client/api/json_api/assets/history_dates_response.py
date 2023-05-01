# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ..generic import DictValue, DictValueSchema
from .history_dates_human import AssetTypeHistoryDates


class HistoryDatesSchema(DictValueSchema):
    """Schema for response from getting valid history dates for all asset types."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return HistoryDates


@dataclasses.dataclass
class HistoryDates(DictValue):
    """Model for response from getting valid history dates for all asset types"""

    parsed: t.ClassVar[dict] = None

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return HistoryDatesSchema

    def __post_init__(self):
        """Dataclass post init."""
        self.parsed = {}
        for asset_type, values in self.value.items():
            obj = AssetTypeHistoryDates(asset_type=asset_type, values=values)
            setattr(self, asset_type, obj)
            self.parsed[asset_type] = obj

    def __str__(self) -> str:
        """Pass."""
        return "\n".join([f"{x!r}" for x in self.parsed.values()])
