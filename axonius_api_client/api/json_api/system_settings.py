# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import dataclasses_json
import marshmallow_jsonapi

from ...exceptions import FeatureNotEnabledError
from ...tools import dt_days_left, dt_parse
from .base import BaseModel, BaseSchemaJson
from .custom_fields import SchemaDatetime, get_field_dc_mm


class SystemSettingsSchema(BaseSchemaJson):
    """Pass."""

    config = marshmallow_jsonapi.fields.Dict(required=True)
    configName = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    config_name = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    pluginId = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")
    prefix = marshmallow_jsonapi.fields.Str(load_default="", dump_default="")

    @staticmethod
    def get_model_cls() -> t.Any:
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
    def get_schema_cls() -> t.Any:
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
    def get_model_cls() -> t.Any:
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
    def get_schema_cls() -> t.Any:
        """Pass."""
        return SystemSettingsUpdateSchema


class FeatureFlagsSchema(SystemSettingsSchema):
    """Pass."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return FeatureFlags


@dataclasses.dataclass
class FeatureFlags(SystemSettings):
    """Pass."""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return FeatureFlagsSchema

    @property
    def has_cloud_compliance(self) -> bool:
        """Get the status of cloud compliance module being enabled."""
        return self._cloud_compliance.get("enabled", False)

    def data_scope_check(self):
        """Check if data scope feature flag is enabled.

        Raises:
            FeatureNotEnabledError: if data scope feature flag is not enabled
        """
        if not self.data_scopes_enabled:
            raise FeatureNotEnabledError(name="Data Scopes")

    @property
    def saas_enabled(self) -> bool:
        """Get the status of SAAS & tunnel support being enabled."""
        return self.config.get("enable_saas", False)

    @property
    def data_scopes_enabled(self) -> bool:
        """Get the status of data scopes being enabled."""
        return self._data_scopes.get("enabled", False)

    @property
    def data_scopes_max(self) -> t.Optional[int]:
        """Get the max number of data scopes allowed."""
        return self._data_scopes.get("queries_limit", None)

    @property
    def _data_scopes(self) -> dict:
        return self.config.get("data_scope") or {}

    @property
    def _cloud_compliance(self) -> dict:
        return self.config.get("cloud_compliance") or {}

    @property
    def trial_expiry_dt(self) -> t.Optional[datetime.datetime]:
        """Get the trial expiration date."""
        expiry = self.config["trial_end"]
        return dt_parse(obj=expiry) if expiry else None

    @property
    def trial_expiry_in_days(self) -> t.Optional[int]:
        """Get the number of days left for the trial."""
        return dt_days_left(obj=self.trial_expiry_dt)

    @property
    def license_expiry_dt(self) -> t.Optional[datetime.datetime]:
        """Get the license expiration date."""
        expiry = self.config["expiry_date"]
        return dt_parse(obj=expiry) if expiry else None

    @property
    def license_expiry_in_days(self) -> t.Optional[int]:
        """Get the number of days left for the license."""
        return dt_days_left(obj=self.license_expiry_dt)


@dataclasses.dataclass
class FileSpec(dataclasses_json.DataClassJsonMixin):
    """Pass."""

    uuid: str
    filename: str


@dataclasses.dataclass
class CertificateUpdateRequest(BaseModel):
    """Pass."""

    cert_file: FileSpec
    enabled: bool
    hostname: str
    private_key: FileSpec
    passphrase: str = ""

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return None


class CertificateDetailsSchema(BaseSchemaJson):
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
    def get_model_cls() -> t.Any:
        """Pass."""
        return CertificateDetails


@dataclasses.dataclass
class CertificateDetails(BaseModel):
    """Pass."""

    issued_to: str
    alternative_names: t.List[str]
    issued_by: str
    sha1_fingerprint: str
    expires_on: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True), default=None
    )
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def _str_properties() -> t.List[str]:
        """Pass."""
        return ["issued_to", "alternative_names", "issued_by", "sha1_fingerprint", "expires_on"]

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CertificateDetailsSchema


class CertificateConfigSchema(BaseSchemaJson):
    """Pass."""

    certificate_verify = marshmallow_jsonapi.fields.Dict(
        load_default={}, dump_default={}, allow_none=True
    )
    mutual_tls = marshmallow_jsonapi.fields.Dict(load_default={}, dump_default={}, allow_none=True)
    ssl_trust = marshmallow_jsonapi.fields.Dict(load_default={}, dump_default={}, allow_none=True)

    class Meta:
        """Pass."""

        type_ = "certificate_config_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return CertificateConfig


@dataclasses.dataclass
class CertificateConfig(BaseModel):
    """Pass."""

    certificate_verify: t.Optional[dict] = dataclasses.field(default_factory=dict)
    mutual_tls: t.Optional[dict] = dataclasses.field(default_factory=dict)
    ssl_trust: t.Optional[dict] = dataclasses.field(default_factory=dict)
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CertificateConfigSchema
