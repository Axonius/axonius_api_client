# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type

import marshmallow

from ...tools import dt_now, dt_parse, trim_float
from ..models import DataModel, DataSchema
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm


class RemoteSupportSchema(DataSchema):
    """Pass."""

    provision = SchemaBool()
    analytics = SchemaBool()
    troubleshooting = SchemaBool()
    timeout = SchemaDatetime(allow_none=True)
    type = marshmallow.fields.Str(default="maintenance")
    _id = marshmallow.fields.Str()

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return RemoteSupport


@dataclasses.dataclass
class RemoteSupport(DataModel):
    """Pass."""

    provision: bool
    analytics: bool
    troubleshooting: bool
    timeout: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    type: str = "maintenance"
    _id: str = ""

    @staticmethod
    def _str_properties() -> List[str]:
        return [
            "enabled",
            "enabled_temporarily",
            "enabled_permanently",
            "temporary_expiry_date",
            "temporary_expires_in_hours",
            "analytics_enabled",
            "remote_access_enabled",
        ]

    @property
    def enabled_permanently(self) -> bool:
        """Pass."""
        return self.provision

    @property
    def enabled_temporarily(self) -> bool:
        """Pass."""
        return bool(self.timeout)

    @property
    def enabled(self) -> bool:
        """Pass."""
        return self.enabled_permanently or self.enabled_temporarily

    @property
    def temporary_expiry_date(self) -> Optional[datetime.datetime]:
        """Pass."""
        value = self.timeout
        if value:
            return dt_parse(value)
        return None

    @property
    def temporary_expires_in_hours(self) -> Optional[float]:
        """Pass."""
        value = self.temporary_expiry_date
        if value:
            return trim_float(value=(value - dt_now()).total_seconds() / 60 / 60)
        return None

    @property
    def analytics_enabled(self) -> bool:
        """Pass."""
        return self.enabled and self.analytics

    @property
    def remote_access_enabled(self) -> bool:
        """Pass."""
        return self.enabled and self.troubleshooting

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return RemoteSupportSchema


class UpdatePermanentRequestSchema(DataSchema):
    """Pass."""

    provision = SchemaBool()

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return UpdatePermanentRequest


@dataclasses.dataclass
class UpdatePermanentRequest(DataModel):
    """Pass."""

    provision: bool

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return UpdatePermanentRequestSchema


class UpdateAnalyticsRequestSchema(DataSchema):
    """Pass."""

    analytics = SchemaBool()

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return UpdateAnalyticsRequest


@dataclasses.dataclass
class UpdateAnalyticsRequest(DataModel):
    """Pass."""

    analytics: bool

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return UpdateAnalyticsRequestSchema


class UpdateTroubleshootingRequestSchema(DataSchema):
    """Pass."""

    troubleshooting = SchemaBool()

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return UpdateTroubleshootingRequest


@dataclasses.dataclass
class UpdateTroubleshootingRequest(DataModel):
    """Pass."""

    troubleshooting: bool

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return UpdateTroubleshootingRequestSchema


class UpdateTemporaryRequestSchema(DataSchema):
    """Pass."""

    duration = marshmallow.fields.Int(validate=marshmallow.validate.Range(min=1))

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return UpdateTemporaryRequest


@dataclasses.dataclass
class UpdateTemporaryRequest(DataModel):
    """Pass."""

    duration: int

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return UpdateTemporaryRequestSchema


@dataclasses.dataclass
class UpdateTemporaryResponse(DataModel):
    """Pass."""

    timeout: str
