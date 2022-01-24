# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import Optional, Type, List

import dataclasses_json
import marshmallow_jsonapi

from .custom_fields import SchemaDatetime, get_field_dc_mm
from ...tools import dt_days_left, dt_parse
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .generic import ApiBase


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


@dataclasses.dataclass
class FileSpec(dataclasses_json.DataClassJsonMixin):
    uuid: str
    filename: str


@dataclasses.dataclass
class SSLUpdateRequest(BaseModel):
    """Pass."""

    cert_file: FileSpec
    enabled: bool
    hostname: str
    private_key: FileSpec

    passphrase: str = ""


class SSLCertificateSchema(BaseSchemaJson):
    """Pass."""

    issued_to = marshmallow_jsonapi.fields.Str()
    alternative_names = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    expires_on = SchemaDatetime(allow_none=True)
    issued_by = marshmallow_jsonapi.fields.Str()
    sha1_fingerprint = marshmallow_jsonapi.fields.Str()

    class Meta:
        """Pass."""

        type_ = "certificate_schema"

    @staticmethod
    def get_model_cls() -> Optional[Type[BaseModel]]:
        """Pass."""
        return SSLCertificate


@dataclasses.dataclass
class SSLCertificate(BaseModel):
    """Pass."""

    issued_to: str
    alternative_names: List[str]
    issued_by: str
    sha1_fingerprint: str
    expires_on: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return SSLCertificateSchema
