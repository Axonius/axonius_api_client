# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow

from .count_operator import OperatorTypes
from .custom_fields import get_schema_dc


class DurationOperatorSchema(marshmallow.Schema):
    """Duration operator schema."""

    type = marshmallow.fields.Str(
        load_default=None,
        dump_default=None,
        description="Duration Operator type",
        validate=marshmallow.validate.OneOf([None, *[x.name for x in OperatorTypes]]),
    )
    seconds = marshmallow.fields.Integer(
        load_default=None,
        dump_default=None,
        description="Amount of seconds",
        allow_none=True,
    )
    seconds_float = marshmallow.fields.Number(
        load_default=None,
        dump_default=None,
        description="Amount of seconds as float",
        allow_none=True,
    )

    class Meta:
        """Marshmallow JSONAPI meta class."""

        type_ = "duration_operator_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return DurationOperator


@dataclasses.dataclass(repr=False)
class DurationOperator:
    """Duration operator dataclass."""

    type: t.Optional[str] = get_schema_dc(
        schema=DurationOperatorSchema,
        key="type",
        default=None,
    )
    seconds: t.Optional[int] = get_schema_dc(
        schema=DurationOperatorSchema,
        key="seconds",
        default=None,
    )
    seconds_float: t.Optional[float] = get_schema_dc(
        schema=DurationOperatorSchema,
        key="seconds_float",
        default=None,
    )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return DurationOperatorSchema
