# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import enum
from typing import Optional

import marshmallow

from .base import BaseModel
from .custom_fields import get_field_dc_mm


class OperatorTypes(enum.Enum):
    """Possible types for defining operators in mongo."""

    equal = "$eq"
    greater = "$gt"
    less = "$lt"


class CountOperatorSchema(marshmallow.Schema):
    """Pass."""

    type = marshmallow.fields.Str(
        load_default=None,
        dump_default=None,
        allow_none=True,
        validate=marshmallow.validate.OneOf([x.name for x in OperatorTypes]),
    )
    count = marshmallow.fields.Integer(dump_default=None, load_default=None, allow_none=True)

    class Meta:
        """Pass."""

        type_ = "count_operator_schema"


COUNT_OPERATOR_SCHEMA = CountOperatorSchema()


@dataclasses.dataclass
class CountOperator(BaseModel):
    """Pass."""

    type: Optional[str] = get_field_dc_mm(
        mm_field=COUNT_OPERATOR_SCHEMA.fields["type"], default=None
    )
    count: Optional[int] = get_field_dc_mm(
        mm_field=COUNT_OPERATOR_SCHEMA.fields["count"], default=None
    )
