# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import List, Optional, Type

import marshmallow_jsonapi

from ...http import Http
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaBool, get_schema_dc


class MetadataSchema(BaseSchemaJson):
    """Pass."""

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return Metadata

    @classmethod
    def load_response(cls, data: dict, http: Http, **kwargs):
        """Pass."""
        # PBUG: Metadata returns None for data
        if data["data"] is None:
            data["data"] = {"type": cls.Meta.type_, "attributes": {}}

        return super().load_response(data=data, http=http, **kwargs)

    class Meta:
        """Pass."""

        type_ = "metadata_schema"


@dataclasses.dataclass
class Metadata(BaseModel):
    """Pass."""

    document_meta: dict = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return MetadataSchema


class BoolValueSchema(BaseSchemaJson):
    """Pass."""

    value = SchemaBool(required=True)

    class Meta:
        """Pass."""

        type_ = "bool_value_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return BoolValue


@dataclasses.dataclass
class BoolValue(BaseModel):
    """Pass."""

    value: bool

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return BoolValueSchema


class NameSchema(BaseSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()

    class Meta:
        """Pass."""

        type_ = "name_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return Name


@dataclasses.dataclass
class Name(BaseModel):
    """Pass."""

    name: bool

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return NameSchema


class IntValueSchema(BaseSchemaJson):
    """Pass."""

    value = marshmallow_jsonapi.fields.Int(required=True)

    class Meta:
        """Pass."""

        type_ = "int_value_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return IntValue


@dataclasses.dataclass
class IntValue(BaseModel):
    """Pass."""

    value: int

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return IntValueSchema


class ApiBaseSchema(BaseSchemaJson):
    """Pass."""

    id = marshmallow_jsonapi.fields.Str(required=True)

    class Meta:
        """Pass."""

        type_ = "base_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return ApiBase


@dataclasses.dataclass
class ApiBase(BaseModel):
    """Pass."""

    id: str
    filename: Optional[str] = None

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return ApiBaseSchema

    def to_dict_file_spec(self):
        """Pass."""
        return {"uuid": self.id, "filename": self.filename}


class StrValueSchema(BaseSchemaJson):
    """Pass."""

    value = marshmallow_jsonapi.fields.Str(required=True)

    class Meta:
        """Pass."""

        type_ = "string_value_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return StrValue


@dataclasses.dataclass
class StrValue(BaseModel):
    """Pass."""

    value: str

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return StrValueSchema


class ListValueSchema(BaseSchemaJson):
    """Pass."""

    value = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())

    class Meta:
        """Pass."""

        type_ = "list_value_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return ListValue


@dataclasses.dataclass
class ListValue(BaseModel):
    """Pass."""

    value: List[str] = get_schema_dc(schema=ListValueSchema, key="value", default_factory=list)

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return ListValueSchema


class ListDictValueSchema(BaseSchemaJson):
    """Pass."""

    value = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "list_value_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return ListDictValue


@dataclasses.dataclass
class ListDictValue(BaseModel):
    """Pass."""

    value: List[str] = get_schema_dc(schema=ListDictValueSchema, key="value", default_factory=list)

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return ListDictValueSchema


class DictValueSchema(BaseSchemaJson):
    """Pass."""

    value = marshmallow_jsonapi.fields.Dict()

    class Meta:
        """Pass."""

        type_ = "dict_value_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return DictValue


@dataclasses.dataclass
class DictValue(BaseModel):
    """Pass."""

    value: dict

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return DictValueSchema


class DeletedSchema(BaseSchemaJson):
    """Pass."""

    deleted = marshmallow_jsonapi.fields.Int()

    class Meta:
        """Pass."""

        type_ = "deleted_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return Deleted


@dataclasses.dataclass
class Deleted(BaseModel):
    """Pass."""

    deleted: int

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return DeletedSchema


@dataclasses.dataclass
class PrivateRequest(BaseModel):
    """Pass."""

    private: bool = False

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:
        """Pass."""
        return PrivateRequestSchema


class PrivateRequestSchema(BaseSchemaJson):
    """Pass."""

    private = marshmallow_jsonapi.fields.Bool(load_default=False, dump_default=False)

    class Meta:
        """Pass."""

        type_ = "private_schema"

    @staticmethod
    def get_model_cls() -> type:
        """Pass."""
        return PrivateRequest
