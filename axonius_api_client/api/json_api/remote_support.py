# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type

import marshmallow

from ...tools import dt_now, dt_parse, trim_float
from .base import BaseModel, BaseSchema
from .custom_fields import SchemaBool, SchemaDatetime, get_field_dc_mm


class RemoteSupportSchema(BaseSchema):
    """Pass."""

    provision = SchemaBool()
    analytics = SchemaBool()
    troubleshooting = SchemaBool()
    timeout = SchemaDatetime(allow_none=True)
    type = marshmallow.fields.Str(default="maintenance")
    _id = marshmallow.fields.Str()

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return RemoteSupport


@dataclasses.dataclass
class RemoteSupport(BaseModel):
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
    def get_model_cls() -> type:
        """Pass."""
        return RemoteSupportSchema


class UpdatePermanentRequestSchema(BaseSchema):
    """Pass."""

    provision = SchemaBool()

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return UpdatePermanentRequest


@dataclasses.dataclass
class UpdatePermanentRequest(BaseModel):
    """Pass."""

    provision: bool

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return UpdatePermanentRequestSchema


class UpdateAnalyticsRequestSchema(BaseSchema):
    """Pass."""

    analytics = SchemaBool()

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return UpdateAnalyticsRequest


@dataclasses.dataclass
class UpdateAnalyticsRequest(BaseModel):
    """Pass."""

    analytics: bool

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return UpdateAnalyticsRequestSchema


class UpdateTroubleshootingRequestSchema(BaseSchema):
    """Pass."""

    troubleshooting = SchemaBool()

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return UpdateTroubleshootingRequest


@dataclasses.dataclass
class UpdateTroubleshootingRequest(BaseModel):
    """Pass."""

    troubleshooting: bool

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return UpdateTroubleshootingRequestSchema


class UpdateTemporaryRequestSchema(BaseSchema):
    """Pass."""

    duration = marshmallow.fields.Int(validate=marshmallow.validate.Range(min=1))

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return UpdateTemporaryRequest


@dataclasses.dataclass
class UpdateTemporaryRequest(BaseModel):
    """Pass."""

    duration: int

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return UpdateTemporaryRequestSchema


@dataclasses.dataclass
class UpdateTemporaryResponse(BaseModel):
    """Pass."""

    timeout: str
