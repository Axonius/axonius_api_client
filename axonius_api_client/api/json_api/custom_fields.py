# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import bson
import dataclasses_json
import dateutil
import dateutil.parser
import dateutil.tz
import marshmallow
from marshmallow import validate as marshmallow_validate

from ...tools import coerce_bool, listify


class UnionField(marshmallow.fields.Field):
    """Field that deserializes multi-type input data to app-level objects."""

    def __init__(self, types: t.List[t.Type] = None, *args, **kwargs) -> None:
        """Pass."""
        super().__init__(*args, **kwargs)
        if types:
            self.types = listify(types)
        else:
            raise AttributeError("No types provided on union field")

    @property
    def types_str(self) -> str:
        """Pass."""
        return ", ".join([str(i) for i in self.types])

    def _deserialize(self, value, attr, data, **kwargs):
        if bool([isinstance(value, i) for i in self.types if isinstance(value, i)]):
            return value
        else:
            raise marshmallow.ValidationError(
                f"Field should be any of the following types: {self.types_str}"
            )


def load_date(value: t.Optional[t.Union[str, datetime.datetime]]) -> t.Optional[datetime.datetime]:
    """Pass."""
    if not isinstance(value, datetime.datetime):
        value = dateutil.parser.parse(value)

    if not value.tzinfo:
        value = value.replace(tzinfo=dateutil.tz.tzutc())
    return value


def dump_date(value: t.Optional[t.Union[str, datetime.datetime]]) -> t.Optional[str]:
    """Pass."""
    if isinstance(value, datetime.datetime):
        if not value.tzinfo:
            value = value.replace(tzinfo=dateutil.tz.tzutc())

        value = value.isoformat()

    return value


class SchemaBool(marshmallow.fields.Bool):
    """Support parsing boolean as strings/etc."""

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None and self.allow_none:
            return None

        try:
            return coerce_bool(value)
        except Exception as exc:
            raise marshmallow.ValidationError(str(exc))

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None and self.allow_none:
            return None

        try:
            return coerce_bool(value)
        except Exception as exc:
            raise marshmallow.ValidationError(str(exc))


class SchemaDatetime(marshmallow.fields.DateTime):
    """Field that deserializes multi-type input data to app-level objects."""

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None and self.allow_none:
            return None

        return dump_date(value)

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None and self.allow_none:
            return None

        try:
            return load_date(value)
        except Exception as exc:
            raise marshmallow.ValidationError(str(exc))


class SchemaObjectIDDatetime(marshmallow.fields.DateTime):
    """Field that deserializes multi-type input data to app-level objects."""

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None and self.allow_none:
            return None

        return dump_date(value)

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None and self.allow_none:
            return None

        try:
            return bson.ObjectId(value).generation_time.replace(tzinfo=dateutil.tz.tzutc())
        except Exception as exc:
            raise marshmallow.ValidationError(str(exc))


class SchemaPassword(marshmallow.fields.Field):
    """Field that serializes to a string or an array and deserializes to a string or an array."""

    """
    This exists cuz:
        ["unchanged"]
    """

    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        return value


def get_field_str_req(**kwargs):
    """Pass."""
    kwargs.setdefault("required", True)
    kwargs.setdefault("allow_none", False)
    kwargs.setdefault("validate", marshmallow_validate.Length(min=1))
    return marshmallow.fields.Str(**kwargs)


def get_field_dc_mm(mm_field: marshmallow.fields.Field, **kwargs) -> dataclasses.Field:
    """Pass."""
    kwargs["metadata"] = dataclasses_json.config(mm_field=mm_field)
    return dataclasses.field(**kwargs)


def get_schema_dc(schema: t.Type[marshmallow.Schema], key: str, **kwargs) -> dataclasses.Field:
    """Pass."""
    # noinspection PyProtectedMember
    field: marshmallow.fields.Field = schema._declared_fields[key]
    kwargs["mm_field"] = field
    return get_field_dc_mm(**kwargs)


def setdefault(mm_field: marshmallow.fields.Field, attr: str, kwargs: dict) -> dict:
    """Add the default or default factory to kwargs accordingly."""
    default = getattr(mm_field, attr, marshmallow.missing)
    if (
        default is not marshmallow.missing
        and "default" not in kwargs
        and "default_factory" not in kwargs
    ):
        if callable(default):
            kwargs.setdefault("default_factory", default)
        else:
            kwargs.setdefault("default", default)
    return kwargs


def field_from_mm(
    schema: t.Union[t.Type[marshmallow.Schema], marshmallow.Schema], key: str, **kwargs
) -> dataclasses.Field:
    """Pass."""
    if isinstance(schema, marshmallow.Schema):
        if key not in schema.fields:
            valids = "\n" + "\n".join(f" - {k}: {v}" for k, v in schema.fields.items())
            raise ValueError(f"Key {key!r} not found in schema {schema}\nValids: {valids}")

        mm_field: marshmallow.fields.Field = schema.fields[key]
    else:
        # noinspection PyProtectedMember
        mm_field: marshmallow.fields.Field = schema._declared_fields[key]
    if mm_field.required is not True:
        kwargs = setdefault(mm_field=mm_field, attr="load_default", kwargs=kwargs)
        kwargs = setdefault(mm_field=mm_field, attr="dump_default", kwargs=kwargs)
    kwargs["metadata"] = dataclasses_json.config(mm_field=mm_field, metadata=kwargs.get("metadata"))
    dc_field: dataclasses.Field = dataclasses.field(**kwargs)
    return dc_field


def validator_wrapper(fn: callable) -> callable:
    """Pass."""

    def validator(value):
        """Pass."""
        try:
            return fn(value=value)
        except Exception as exc:
            raise marshmallow.ValidationError(str(exc))

    return validator
