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
    configName = marshmallow_jsonapi.fields.Str(default="", missing="")
    config_name = marshmallow_jsonapi.fields.Str(default="", missing="")
    pluginId = marshmallow_jsonapi.fields.Str(default="", missing="")
    prefix = marshmallow_jsonapi.fields.Str(default="", missing="")

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
    configName = marshmallow_jsonapi.fields.Str(default="", missing="")
    config_name = marshmallow_jsonapi.fields.Str(default="", missing="")
    pluginId = marshmallow_jsonapi.fields.Str(default="", missing="")
    prefix = marshmallow_jsonapi.fields.Str(default="", missing="")

    class Meta:
        """Pass."""

        type_ = "settings_schema"


@dataclasses.dataclass
class SystemSettingsGuiUpdate(BaseModel):
    """Pass."""

    config: dict
    configName: str = "GuiService"
    pluginId: str = "gui"

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SystemSettingsUpdateSchema


@dataclasses.dataclass
class SystemSettingsIdentityProvidersUpdate(BaseModel):
    """Pass."""

    config: dict
    configName: str = "IdentityProviders"
    pluginId: str = "gui"

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SystemSettingsUpdateSchema


@dataclasses.dataclass
class SystemSettingsLifecycleUpdate(BaseModel):
    """Pass."""

    config: dict
    configName: str = "SystemSchedulerService"
    pluginId: str = "system_scheduler"

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SystemSettingsUpdateSchema


@dataclasses.dataclass
class SystemSettingsGlobalUpdate(BaseModel):
    """Pass."""

    config: dict
    configName: str = "CoreService"
    pluginId: str = "core"

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
        return self.config["cloud_compliance"]["enabled"]

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
