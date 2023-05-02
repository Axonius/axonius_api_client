# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow

from ...tools import (
    get_hint_type,
    get_mm_description,
    get_mm_field,
    is_nested_schema,
    is_subclass,
    listify,
    score_prefix,
)
from . import base


def is_complex_field(value: t.Union[dataclasses.Field, marshmallow.fields.Field]) -> bool:
    """Check if a field is a complex field.

    Args:
        value: The field to check.

    Returns:
        bool: True if the field is complex.
    """
    if isinstance(value, marshmallow.fields.Field):
        return is_nested_schema(value=value)
    elif isinstance(value, dataclasses.Field):
        if is_subclass(get_hint_type(value.type), BaseModel):
            return True
        return is_nested_schema(value=get_mm_field(value))
    return False


class BaseSchema(base.BaseSchema):
    """Version2 of BaseSchema."""

    @marshmallow.post_dump()
    def post_dump(self, data, **kwargs):
        """Post dump."""
        ret: t.Dict[str, t.Any] = {
            k.name: data.pop(k.name) for k in self.get_model_fields() if k.name in data
        }
        ret.update(data)
        return ret


class BaseModel(base.BaseModel):
    """Mixins to help with serialization."""

    SCHEMA: t.ClassVar[marshmallow.Schema]

    def to_dict(self, explode: bool = False, **kwargs) -> dict:
        """Convert the model to a dictionary.

        Returns:
            dict: The dictionary.
        """
        return self._dump(value=self, explode=explode)

    @classmethod
    def to_dicts(
        cls,
        values: t.Any,
        explode: bool = False,
        schemas: bool = False,
        as_csv: bool = False,
    ) -> t.Generator[dict, None, None]:
        """Convert a list of models to a list of dicts.

        Args:
            values: The values to convert.
            explode: Explode the values.
            schemas: Include the schemas.
            as_csv: Return the data as csv.

        Yields:
            dict: if as_csv is True, the headers, then the schemas if schemas=True,
                and then the converted values.
            dict: if as_csv is False, the schemas if schemas=True and then the
                converted values.
        """
        values: t.List[t.Any] = listify(values)
        fields: t.Dict[str, dataclasses.Field] = cls._get_fields_explode(explode=explode)

        if as_csv:
            yield {k: k for k in fields}
            if schemas:
                yield from cls._get_fields_out_csv(fields=fields)
        elif schemas:
            yield {"schemas": cls._get_fields_out(fields=fields)}

        for value in values:
            if isinstance(value, cls):
                value_dicts: t.Union[dict, t.List[dict]] = value.to_dict(explode=explode)
                if isinstance(value_dicts, list):
                    yield from value_dicts
                else:
                    yield value_dicts

    @classmethod
    def _get_fields_out(cls, fields: t.Dict[str, dataclasses.Field]) -> dict:
        """Get the fields for the to_dict."""
        fields_out: dict = {}
        for k, v in fields.items():
            mm_field = get_mm_field(v)
            fields_out[k] = {
                "name": k,
                "type": str(v.type),
                "description": get_mm_description(mm_field),
                "allow_none": mm_field.allow_none,
                "required": mm_field.required,
                "default": str(mm_field.load_default),
            }
        return fields_out

    @classmethod
    def _get_fields_out_csv(cls, fields: t.Dict[str, dataclasses.Field]) -> t.List[dict]:
        """Get the fields for the to_dict."""
        return [
            {k: str(v.type) for k, v in fields.items()},
            {k: get_mm_description(v) for k, v in fields.items()},
        ]

    @classmethod
    def _get_fields_explode(
        cls, explode: bool = False, prefix: t.Optional[t.List[str]] = None
    ) -> t.Dict[str, dataclasses.Field]:
        """Get the headers for the CSV.

        Args:
            explode: Explode the headers for fields that are lists of complex fields.
            prefix: Prefix to add to the headers for complex fields.

        Returns:
            t.Dict[str, dataclasses.Field]: The headers.
        """
        schemas: t.Dict[str, dataclasses.Field] = {}
        prefix: t.List[str] = listify(prefix)

        for field in cls._get_fields():
            if not field.repr:
                continue
            if is_complex_field(field) and explode:
                _type: t.Optional[t.Type["BaseModel"]] = get_hint_type(field.type)
                # noinspection PyProtectedMember
                if is_subclass(_type, BaseModel):
                    _schemas = _type._get_fields_explode(explode=True, prefix=[field.name])
                    schemas.update(_schemas)
                else:
                    schemas[score_prefix(field.name, prefix=prefix)] = field
            else:
                schemas[score_prefix(field.name, prefix=prefix)] = field
        return schemas

    @classmethod
    def _get_fields_complex(cls) -> t.List[dataclasses.Field]:
        """Get a list of fields that are lists of complex nested objects.

        Returns:
            t.List[str]: The list of complex fields.
        """
        return [f for f in cls._get_fields() if is_complex_field(f)]

    @classmethod
    def _dump(
        cls, value: t.Any, many: t.Optional[bool] = None, explode: bool = False
    ) -> t.Union[dict, t.List[dict]]:
        """Pass."""
        many: bool = many if isinstance(many, bool) else isinstance(value, (list, tuple))
        data: t.Union[dict, t.List[dict]] = cls.SCHEMA.dump(value, many=many)
        if explode and cls._get_fields_complex():
            data: t.List[dict] = list(cls._explode(data=data))
        return data

    @classmethod
    def _explode(cls, data: t.Union[dict, t.List[dict]]) -> t.Generator[dict, None, None]:
        """Explode a dict or list of dict multiple rows per complex value.

        Args:
            data: The dict or list of dict to explode.

        Returns:
            t.List[dict]: The exploded data.
        """
        if isinstance(data, (list, tuple)):
            for x in data:
                yield from cls._explode(x)

        if isinstance(data, dict):
            for field in cls._get_fields_complex():
                values: t.List[dict] = listify(data.pop(field.name, []))
                yield from [
                    {**data, **{f"{field.name}_{k}": v for k, v in x.items()}} for x in values
                ] if values else [data]
