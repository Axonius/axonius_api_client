# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import Optional, Type

import marshmallow_jsonapi

from ...tools import dt_days_left, dt_parse
from .base import BaseModel, BaseSchema, BaseSchemaJson


class SystemSettingsSchema(BaseSchemaJson):
    """Pass."""

    config = marshmallow_jsonapi.fields.Dict(required=True)
    configName = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    config_name = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    pluginId = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    prefix = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return SystemSettings

    class Meta:
        """Pass."""

        type_ = "settings_schema"


@dataclasses.dataclass
class SystemSettings(BaseModel):
    """Pass."""

    config: dict
    configName: str = ""
    config_name: str = ""
    pluginId: str = ""
    prefix: str = ""
    document_meta: dict = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SystemSettingsSchema


class SystemSettingsUpdateSchema(BaseSchemaJson):
    """Pass."""

    config = marshmallow_jsonapi.fields.Dict(required=True)
    configName = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    config_name = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    pluginId = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    prefix = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")

    class Meta:
        """Pass."""

        type_ = "settings_schema"

    @staticmethod
    def get_model_cls() -> Optional[type]:
        """Pass."""
        return SystemSettingsUpdate


@dataclasses.dataclass
class SystemSettingsUpdate(BaseModel):
    """Pass."""

    config: dict
    configName: str = ""
    config_name: str = ""
    pluginId: str = ""
    prefix: str = ""

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SystemSettingsUpdateSchema


class FeatureFlagsSchema(SystemSettingsSchema):
    """Pass."""

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return FeatureFlags


@dataclasses.dataclass
class FeatureFlags(SystemSettings):
    """Pass."""

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return FeatureFlagsSchema

    @property
    def has_cloud_compliance(self) -> bool:
        """Get the status of cloud compliance module being enabled."""
        return self._cloud_compliance.get("enabled", False)

    @property
    def asset_scopes_enabled(self) -> bool:
        """Get the status of asset scopes being enabled."""
        return self._asset_scope.get("enabled", False)

    @property
    def asset_scopes_max(self) -> Optional[int]:
        """Get the max number of asset scopes allowed."""
        return self._asset_scope.get("queries_limit", None)

    @property
    def _asset_scope(self) -> dict:
        return self.config.get("data_scope") or {}

    @property
    def _cloud_compliance(self) -> dict:
        return self.config.get("cloud_compliance") or {}

    @property
    def trial_expiry_dt(self) -> Optional[datetime.datetime]:
        """Get the trial expiration date."""
        expiry = self.config["trial_end"]
        return dt_parse(obj=expiry) if expiry else None

    @property
    def trial_expiry_in_days(self) -> Optional[int]:
        """Get the number of days left for the trial."""
        return dt_days_left(obj=self.trial_expiry_dt)

    @property
    def license_expiry_dt(self) -> Optional[datetime.datetime]:
        """Get the license expiration date."""
        expiry = self.config["expiry_date"]
        return dt_parse(obj=expiry) if expiry else None

    @property
    def license_expiry_in_days(self) -> Optional[int]:
        """Get the number of days left for the license."""
        return dt_days_left(obj=self.license_expiry_dt)
