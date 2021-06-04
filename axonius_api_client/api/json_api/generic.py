# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import Optional, Type

import marshmallow_jsonapi

from ..models import DataModel, DataSchema, DataSchemaJson
from .custom_fields import SchemaBool


class MetadataSchema(DataSchemaJson):
    """Pass."""

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return Metadata

    @classmethod
    def _load_response(cls, data: dict, client, api_endpoint, **kwargs):
        """Pass."""
        cls._check_version(data=data, api_endpoint=api_endpoint)

        # PBUG: Metadata returns None for data
        if data["data"] is None:
            data["data"] = {"type": cls.Meta.type_, "attributes": {}}

        return super()._load_response(data=data, client=client, api_endpoint=api_endpoint, **kwargs)

    class Meta:
        """Pass."""

        type_ = "metadata_schema"


@dataclasses.dataclass
class Metadata(DataModel):
    """Pass."""

    document_meta: dict = dataclasses.field(default_factory=dict)

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return MetadataSchema


class BoolValueSchema(DataSchemaJson):
    """Pass."""

    value = SchemaBool(required=True)

    class Meta:
        """Pass."""

        type_ = "bool_value_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return BoolValue


@dataclasses.dataclass
class BoolValue(DataModel):
    """Pass."""

    value: bool

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return BoolValueSchema


class IntValueSchema(DataSchemaJson):
    """Pass."""

    value = marshmallow_jsonapi.fields.Int(required=True)

    class Meta:
        """Pass."""

        type_ = "int_value_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return IntValue


@dataclasses.dataclass
class IntValue(DataModel):
    """Pass."""

    value: int

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return IntValueSchema


class StrValueSchema(DataSchemaJson):
    """Pass."""

    value = marshmallow_jsonapi.fields.Str(required=True)

    class Meta:
        """Pass."""

        type_ = "string_value_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return StrValue


@dataclasses.dataclass
class StrValue(DataModel):
    """Pass."""

    value: str

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return StrValueSchema


class NameValueSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)

    class Meta:
        """Pass."""

        type_ = "name_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return NameValue


@dataclasses.dataclass
class NameValue(DataModel):
    """Pass."""

    name: str

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return NameValueSchema


class DictValueSchema(DataSchemaJson):
    """Pass."""

    value = marshmallow_jsonapi.fields.Dict()

    class Meta:
        """Pass."""

        type_ = "dict_value_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return DictValue


@dataclasses.dataclass
class DictValue(DataModel):
    """Pass."""

    value: dict

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return DictValueSchema


class DeletedSchema(DataSchemaJson):
    """Pass."""

    deleted = marshmallow_jsonapi.fields.Int()

    class Meta:
        """Pass."""

        type_ = "deleted_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return Deleted


@dataclasses.dataclass
class Deleted(DataModel):
    """Pass."""

    deleted: int

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return DeletedSchema


# TBD: gone from cortex 03/22/21
# @dataclasses.dataclass
# class PrivateRequest(DataModel):
#     """Pass."""

#     private: bool = False

#     @staticmethod
#     def _get_schema_cls() -> Optional[Type[DataSchema]]:
#         """Pass."""
#         return PrivateRequestSchema


# class PrivateRequestSchema(DataSchemaJson):
#     """Pass."""

#     private = marshmallow_jsonapi.fields.Bool(missing=False)

#     class Meta:
#         """Pass."""

#         type_ = "private_schema"

#     @staticmethod
#     def _get_model_cls() -> type:
#         """Pass."""
#         return PrivateRequest
