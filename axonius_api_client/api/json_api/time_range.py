# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import typing as t

import marshmallow

from ...data import BaseEnum
from ...exceptions import ApiError
from ...tools import coerce_int, dt_now, dt_parse
from .base import BaseModel
from .custom_fields import SchemaDatetime, get_field_dc_mm, validator_wrapper


class DateTypes(BaseEnum):
    """Possible types of a date config for the time range."""

    absolute = "absolute"
    relative = "relative"

    @classmethod
    def get_default(cls) -> "str":
        """Pass."""
        return cls.absolute.name


class UnitTypes(BaseEnum):
    """Possible units for defining a relative time range."""

    day = 1
    week = 7
    month = 30
    year = 365

    @classmethod
    def get_default(cls) -> "str":
        """Pass."""
        return cls.day.name


class TimeRangeSchema(marshmallow.Schema):
    """Pass."""

    type = marshmallow.fields.Str(
        load_default=DateTypes.get_default(),
        dump_default=DateTypes.get_default(),
        allow_none=True,
        validate=validator_wrapper(DateTypes.get_name_by_value),
    )
    unit = marshmallow.fields.Str(
        dump_default=UnitTypes.get_default(),
        load_default=UnitTypes.get_default(),
        allow_none=True,
        validate=validator_wrapper(UnitTypes.get_name_by_value),
    )
    date_from = SchemaDatetime(dump_default=None, load_default=None, allow_none=True)
    date_to = SchemaDatetime(dump_default=None, load_default=None, allow_none=True)
    count = marshmallow.fields.Integer(dump_default=None, load_default=None, allow_none=True)

    class Meta:
        """Pass."""

        type_ = "time_range_schema"


@dataclasses.dataclass
class TimeRange(BaseModel):
    """Pass."""

    type: t.Optional[str] = get_field_dc_mm(
        mm_field=TimeRangeSchema._declared_fields["type"], default=DateTypes.get_default()
    )
    unit: t.Optional[str] = get_field_dc_mm(
        mm_field=TimeRangeSchema._declared_fields["unit"], default=UnitTypes.get_default()
    )
    date_from: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=TimeRangeSchema._declared_fields["date_from"], default=None
    )
    date_to: t.Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=TimeRangeSchema._declared_fields["date_to"], default=None
    )
    count: t.Optional[int] = get_field_dc_mm(
        mm_field=TimeRangeSchema._declared_fields["count"], default=None
    )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Pass."""
        return TimeRangeSchema

    @classmethod
    def build(
        cls,
        relative_unit_type: UnitTypes = UnitTypes.get_default(),
        relative_unit_count: t.Optional[int] = None,
        absolute_date_start: t.Optional[datetime.datetime] = None,
        absolute_date_end: t.Optional[datetime.datetime] = None,
    ) -> "TimeRange":
        """Pass."""
        if absolute_date_end and not absolute_date_start:
            raise ApiError(
                "absolute_date_start must also be supplied when absolute_date_end is supplied"
            )

        if absolute_date_start:
            absolute_date_start = dt_parse(absolute_date_start)
            if absolute_date_end:
                absolute_date_end = dt_parse(absolute_date_end)
            else:
                absolute_date_end = dt_now()

            date_type = DateTypes.absolute.name
            relative_unit_type = UnitTypes.get_default()
            relative_unit_count = None
        elif relative_unit_count:
            relative_unit_type = UnitTypes.get_name_by_value(relative_unit_type)
            relative_unit_count = coerce_int(obj=relative_unit_count, min_value=1)

            date_type = DateTypes.relative.name
            absolute_date_start = None
            absolute_date_end = None
        else:
            relative_unit_type = UnitTypes.get_default()
            relative_unit_count = None

            date_type = DateTypes.get_default()
            absolute_date_start = None
            absolute_date_end = None

        return cls(
            type=date_type,
            unit=relative_unit_type,
            count=relative_unit_count,
            date_from=absolute_date_start,
            date_to=absolute_date_end,
        )
