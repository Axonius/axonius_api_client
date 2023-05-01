# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import typing as t

import marshmallow
import marshmallow.validate as mm_validate
import marshmallow.fields as mm_fields

from .count_operator import OperatorTypes
from .custom_fields import field_from_mm
from ...tools import combo_dicts


class DurationOperatorSchema(marshmallow.Schema):
    """Duration operator schema."""

    # noinspection PyTypeChecker
    type = mm_fields.Str(
        load_default=None,
        dump_default=None,
        description="Duration Operator type",
        validate=mm_validate.OneOf([None, *[x.name for x in OperatorTypes]]),
    )
    seconds = mm_fields.Integer(
        load_default=None,
        dump_default=None,
        description="Amount of seconds (deprecated)",
        allow_none=True,
    )
    seconds_float = mm_fields.Number(
        load_default=None,
        dump_default=None,
        description="Amount of seconds as float",
        allow_none=True,
    )

    class Meta:
        """Marshmallow JSONAPI metaclass."""

        type_ = "duration_operator_schema"

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return DurationOperator


SCHEMA = DurationOperatorSchema()


@dataclasses.dataclass(repr=False)
class DurationOperator:
    """Model for duration operator."""

    type: t.Optional[str] = field_from_mm(SCHEMA, "type")
    seconds: t.Optional[int] = field_from_mm(SCHEMA, "seconds")
    seconds_float: t.Optional[float] = field_from_mm(SCHEMA, "seconds_float")

    @classmethod
    def load_if_needed(cls, value: t.Any) -> t.Any:
        """Pass through if already an instance of this model, else load from dict."""
        if isinstance(value, cls):
            return value
        return cls(**combo_dicts(value))

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return DurationOperatorSchema
