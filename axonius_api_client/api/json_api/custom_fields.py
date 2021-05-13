# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type, Union

import dataclasses_json
import dateutil
import marshmallow
import marshmallow_jsonapi

from ...tools import coerce_bool

DT_FMT = "%Y-%m-%dT%H:%M:%S%z"


def load_date(value: Optional[Union[str, datetime.datetime]]) -> Optional[datetime.datetime]:
    """Pass."""
    if not isinstance(value, datetime.datetime):
        value = dateutil.parser.parse(value)

    if not value.tzinfo:
        value = value.replace(tzinfo=dateutil.tz.tzutc())
    return value


def dump_date(value: Optional[Union[str, datetime.datetime]]) -> Optional[str]:
    """Pass."""
    if isinstance(value, datetime.datetime):
        if not value.tzinfo:
            value = value.replace(tzinfo=dateutil.tz.tzutc())

        value = value.isoformat()

    return value


class SchemaBool(marshmallow_jsonapi.fields.Bool):
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


class SchemaDatetime(marshmallow_jsonapi.fields.DateTime):
    """Field that deserializes multi-type input data to app-level objects."""

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None and self.allow_none:
            return None

        try:
            return dump_date(value)
        except Exception as exc:
            raise marshmallow.ValidationError(str(exc))

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None and self.allow_none:
            return None

        try:
            return load_date(value)
        except Exception as exc:
            raise marshmallow.ValidationError(str(exc))


class SchemaPassword(marshmallow_jsonapi.fields.Field):
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
    kwargs.setdefault("validate", marshmallow.validate.Length(min=1))
    return marshmallow_jsonapi.fields.Str(**kwargs)


def get_field_dc_mm(mm_field: marshmallow.fields.Field, **kwargs) -> dataclasses.Field:
    """Pass."""
    kwargs["metadata"] = dataclasses_json.config(mm_field=mm_field)
    return dataclasses.field(**kwargs)


def get_field_oneof(
    choices: List[str], field: Type[marshmallow.fields.Field] = marshmallow.fields.Str, **kwargs
) -> marshmallow.fields.Field:
    """Pass."""
    kwargs["validate"] = marshmallow.validate.OneOf(choices=choices)
    kwargs.setdefault("required", True)
    return field(**kwargs)
