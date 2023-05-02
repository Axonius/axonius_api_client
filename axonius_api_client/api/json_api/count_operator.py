# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import enum
import typing as t

import marshmallow
import marshmallow.validate as mm_validate
import marshmallow.fields as mm_fields

from .base import BaseModel
from .custom_fields import get_field_dc_mm
from ...tools import bytes_to_str


class OperatorTypes(enum.Enum):
    """Possible types for defining operators in mongo."""

    equal = "$eq"
    greater = "$gt"
    less = "$lt"


class CountOperatorSchema(marshmallow.Schema):
    """Pass."""

    # noinspection PyTypeChecker
    type = mm_fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
        validate=mm_validate.OneOf([None, *[x.name for x in OperatorTypes]]),
    )
    count = mm_fields.Integer(dump_default=None, load_default=None, allow_none=True)

    class Meta:
        """Pass."""

        type_ = "count_operator_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return CountOperator


COUNT_OPERATOR_SCHEMA = CountOperatorSchema()


@dataclasses.dataclass
class CountOperator(BaseModel):
    """Pass."""

    type: t.Optional[str] = get_field_dc_mm(
        mm_field=COUNT_OPERATOR_SCHEMA.fields["type"], default=None
    )
    count: t.Optional[int] = get_field_dc_mm(
        mm_field=COUNT_OPERATOR_SCHEMA.fields["count"], default=None
    )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return CountOperatorSchema


TypeOperator: t.TypeVar = t.TypeVar("TypeOperator", str, bytes, OperatorTypes)


def coerce_operator(value: TypeOperator = OperatorTypes.less) -> str:
    """Coerce a value to an operator."""
    if isinstance(value, OperatorTypes):
        return value.name
    value = bytes_to_str(value)
    if isinstance(value, str):
        value = value.lower().strip()
        for operator in OperatorTypes:
            if value in [operator.value, operator.name]:
                return operator.name
    valids = [f"{x.name} ({x.value})" for x in OperatorTypes]
    valids = "\n" + "\n".join(valids)
    raise ValueError(f"Invalid duration_operator: {value}, valids:{valids}")
