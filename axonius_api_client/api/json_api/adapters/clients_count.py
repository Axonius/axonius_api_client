# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ..base import BaseModel


@dataclasses.dataclass
class AdapterClientsCount(BaseModel):
    """Model for client count data."""

    error_count: t.Optional[int] = None
    inactive_count: t.Optional[int] = None
    success_count: t.Optional[int] = None
    total_count: t.Optional[int] = None

    def __post_init__(self):
        """Pass."""
        for field in self._get_fields():
            if field.name.endswith("_count"):
                value = getattr(self, field.name)
                if value is None:
                    setattr(self, field.name, 0)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this class."""
        return None
