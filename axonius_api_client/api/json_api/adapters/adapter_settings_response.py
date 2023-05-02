# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

from ....constants.adapters import DISCOVERY_NAME, GENERIC_NAME, INGESTION_NAME
from ....parsers.config import parse_schema
from ..generic import Metadata, MetadataSchema


class AdapterSettingsSchema(MetadataSchema):
    """Schema for adapter settings response."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Get the model for this schema."""
        return AdapterSettings

    class Meta:
        """JSONAPI config."""

        type_ = "metadata_schema"


SCHEMA = AdapterSettingsSchema()


@dataclasses.dataclass
class AdapterSettings(Metadata):
    """Model for adapter settings response."""

    SCHEMA: t.ClassVar[MetadataSchema] = SCHEMA

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return AdapterSettingsSchema

    @property
    def type_map(self) -> dict:
        """Pass."""
        ret = {
            "generic": self.schema_config_generic,
            "discovery": self.schema_config_discovery,
        }
        if self.schema_config_specific:
            ret["specific"] = self.schema_config_specific
        return ret

    @property
    def schema_config_specific(self) -> dict:
        """Pass."""
        ret = {}
        if self.schema_specific:
            ret = {
                "schema": self.schema_specific,
                "config": self.config_specific,
                "config_name": self.schema_name_specific,
            }
        return ret

    @property
    def schema_config_discovery(self) -> dict:
        """Pass."""
        ret = {
            "schema": self.schema_discovery,
            "config": self.config_discovery,
            "config_name": self.schema_name_discovery,
        }
        return ret

    @property
    def schema_config_generic(self) -> dict:
        """Pass."""
        ret = {
            "schema": self.schema_generic,
            "config": self.config_generic,
            "config_name": self.schema_name_generic,
        }
        return ret

    @property
    def schema_name_specific(self) -> str:
        """Pass."""
        ret = ""
        skips = [self.schema_name_generic, self.schema_name_discovery, self.schema_name_ingestion]
        if self._meta:
            matches = [x for x in self._meta if x.endswith("Adapter") and x not in skips]
            if matches:
                ret = matches[0]
        return ret

    @property
    def schema_name_ingestion(self) -> str:
        """Pass."""
        ret = INGESTION_NAME
        return ret

    @property
    def schema_name_generic(self) -> str:
        """Pass."""
        ret = GENERIC_NAME
        return ret

    @property
    def schema_name_discovery(self) -> str:
        """Pass."""
        ret = DISCOVERY_NAME
        return ret

    @property
    def _meta(self) -> dict:
        """Pass."""
        ret = self.document_meta["advanced_settings"]
        return ret

    @property
    def _schema_specific(self) -> dict:
        """Pass."""
        ret = {}
        if self.schema_name_specific:
            ret = self._meta[self.schema_name_specific]["schema"]
        return ret

    @property
    def _schema_generic(self) -> dict:
        """Pass."""
        ret = {}
        if self.schema_name_generic:
            ret = self._meta[self.schema_name_generic]["schema"]
        return ret

    @property
    def _schema_discovery(self) -> dict:
        """Pass."""
        ret = {}
        if self.schema_name_discovery:
            ret = self._meta[self.schema_name_discovery]["schema"]
        return ret

    @property
    def schema_specific(self) -> dict:
        """Pass."""
        ret = {}
        if self._schema_specific:
            ret = parse_schema(self._schema_specific)
        return ret

    @property
    def schema_generic(self) -> dict:
        """Pass."""
        ret = {}
        if self._schema_generic:
            ret = parse_schema(self._schema_generic)
        return ret

    @property
    def schema_discovery(self) -> dict:
        """Pass."""
        ret = parse_schema(self._schema_discovery)
        return ret

    @property
    def config_specific(self) -> dict:
        """Pass."""
        ret = {}
        if self.schema_name_specific:
            ret = self._meta[self.schema_name_specific]["config"]
        return ret

    @property
    def config_generic(self) -> dict:
        """Pass."""
        ret = self._meta[self.schema_name_generic]["config"]
        return ret

    @property
    def config_discovery(self) -> dict:
        """Pass."""
        ret = self._meta[self.schema_name_discovery]["config"]
        return ret
