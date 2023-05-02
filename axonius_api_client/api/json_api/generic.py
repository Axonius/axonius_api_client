# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow_jsonapi.fields as mm_fields

from ...http import Http
from .base import BaseModel, BaseSchemaJson
from .custom_fields import SchemaBool, get_schema_dc


class MetadataSchema(BaseSchemaJson):
    """Pass."""

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return Metadata

    # noinspection PyMethodOverriding
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
    def get_schema_cls() -> t.Any:
        """Pass."""
        return MetadataSchema


class BoolValueSchema(BaseSchemaJson):
    """Pass."""

    value = SchemaBool(required=True)

    class Meta:
        """Pass."""

        type_ = "bool_value_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return BoolValue


@dataclasses.dataclass
class BoolValue(BaseModel):
    """Pass."""

    value: bool
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return BoolValueSchema


class NameSchema(BaseSchemaJson):
    """Pass."""

    name = mm_fields.Str()

    class Meta:
        """Pass."""

        type_ = "name_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return Name


@dataclasses.dataclass
class Name(BaseModel):
    """Pass."""

    name: bool
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return NameSchema


class IntValueSchema(BaseSchemaJson):
    """Pass."""

    value = mm_fields.Int(required=True)

    class Meta:
        """Pass."""

        type_ = "int_value_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return IntValue


@dataclasses.dataclass
class IntValue(BaseModel):
    """Pass."""

    value: int
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return IntValueSchema


class ApiBaseSchema(BaseSchemaJson):
    """Pass."""

    id = mm_fields.Str(required=True)

    class Meta:
        """Pass."""

        type_ = "base_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return ApiBase


@dataclasses.dataclass
class ApiBase(BaseModel):
    """Pass."""

    id: str
    filename: t.Optional[str] = None
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return ApiBaseSchema

    def to_dict_file_spec(self):
        """Pass."""
        return {"uuid": self.id, "filename": self.filename}


class StrValueSchema(BaseSchemaJson):
    """Pass."""

    value = mm_fields.Str(required=True)

    class Meta:
        """Pass."""

        type_ = "string_value_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return StrValue


@dataclasses.dataclass
class StrValue(BaseModel):
    """Pass."""

    value: str
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return StrValueSchema


class ListValueSchema(BaseSchemaJson):
    """Pass."""

    value = mm_fields.List(mm_fields.Str())

    class Meta:
        """Pass."""

        type_ = "list_value_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return ListValue


@dataclasses.dataclass
class ListValue(BaseModel):
    """Pass."""

    value: t.List[str] = get_schema_dc(schema=ListValueSchema, key="value", default_factory=list)
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return ListValueSchema


class ListDictValueSchema(BaseSchemaJson):
    """Pass."""

    value = mm_fields.List(mm_fields.Dict())

    class Meta:
        """Pass."""

        type_ = "list_value_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return ListDictValue


@dataclasses.dataclass
class ListDictValue(BaseModel):
    """Pass."""

    value: t.List[str] = get_schema_dc(
        schema=ListDictValueSchema, key="value", default_factory=list
    )
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return ListDictValueSchema


class DictValueSchema(BaseSchemaJson):
    """Pass."""

    value = mm_fields.Dict()

    class Meta:
        """Pass."""

        type_ = "dict_value_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return DictValue


@dataclasses.dataclass
class DictValue(BaseModel):
    """Pass."""

    value: dict
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return DictValueSchema


class DeletedSchema(BaseSchemaJson):
    """Pass."""

    deleted = mm_fields.Int()

    class Meta:
        """Pass."""

        type_ = "deleted_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return Deleted


@dataclasses.dataclass
class Deleted(BaseModel):
    """Pass."""

    deleted: int
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return DeletedSchema


@dataclasses.dataclass
class PrivateRequest(BaseModel):
    """Pass."""

    private: bool = False
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return PrivateRequestSchema


class PrivateRequestSchema(BaseSchemaJson):
    """Pass."""

    private = mm_fields.Bool(load_default=False, dump_default=False)

    class Meta:
        """Pass."""

        type_ = "private_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return PrivateRequest
