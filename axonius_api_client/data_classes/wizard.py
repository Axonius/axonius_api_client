#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import dataclasses
from typing import List, Tuple, Union

from ..constants import NO, YES
from .base import BaseData
from .fields import Operators, OperatorTypeMaps


@dataclasses.dataclass
class ExprTemplates(BaseData):
    bracket_expr: str = "({aqls})"
    complex_expr: str = "({field} == match([{aqls}]))"
    and_text: str = " and "
    or_text: str = " or "
    not_text: str = "not "


@dataclasses.dataclass
class ErrorTemplates(BaseData):
    invalid_choice: str = "Invalid choice {value!r}"
    missing_key: str = "Missing required key"


@dataclasses.dataclass
class Types(BaseData):
    SIMPLE: str = "simple"
    COMPLEX: str = "complex"
    COMPLEX_EXPR: str = "complex_expression"
    BRACKET_EXPR: str = "bracket_expression"


@dataclasses.dataclass
class ValueTypes(BaseData):
    choice: str = "choice"
    complex_expr: str = Types.COMPLEX_EXPR
    bracket_expr: str = Types.BRACKET_EXPR
    field: str = "field"
    sub_field: str = "sub_field"
    string: str = "string"
    field_value: str = "field_value"
    boolean: str = "boolean"


@dataclasses.dataclass
class KeyNames(BaseData):
    field: str = "field"
    sub_field: str = "sub_field"
    value: str = "value"
    section_name: str = "name"
    section_type: str = "type"
    operator: str = "operator"
    not_flag: str = "not_flag"
    complex_expr: str = Types.COMPLEX_EXPR
    bracket_expr: str = Types.BRACKET_EXPR


class Key(BaseData):
    pass


@dataclasses.dataclass
class KeyBase(Key):
    key: str
    example: str
    description: str
    default: str = ""
    value_type: str = ValueTypes.string
    required: bool = True
    _priority: int = 0
    _lower: bool = True
    _strip: bool = True


@dataclasses.dataclass
class KeyBoolean(Key):
    key: str
    description: str
    example: str = "false"
    default: str = "false"
    value_type: str = ValueTypes.boolean
    required: bool = False
    _priority: int = 0
    _lower: bool = True
    _strip: bool = True
    for_true: Tuple[str] = tuple(sorted(list(set([str(x).lower() for x in YES]))))
    for_false: Tuple[str] = tuple(sorted(list(set([str(x).lower() for x in NO]))))


@dataclasses.dataclass
class KeyChoices(Key):
    key: str
    example: str
    description: str
    choices: Union[List[str], dict]
    default: str = ""
    value_type: str = ValueTypes.choice
    required: bool = True
    _priority: int = 0
    _lower: bool = True
    _strip: bool = True


@dataclasses.dataclass
class KeyExpression(Key):
    key: str
    example: str
    description: str
    reference_types: List[str]
    value_type: str
    default: str = ""
    required: bool = True
    _priority: int = 0
    _lower: bool = True
    _strip: bool = True


@dataclasses.dataclass
class Keys(BaseData):
    field: Key = KeyBase(
        key=KeyNames.field,
        value_type=ValueTypes.field,
        example="agg:network_interfaces",
        description="field (column) to use in filter",
        _priority=20,
    )
    sub_field: Key = KeyBase(
        key=KeyNames.sub_field,
        value_type=ValueTypes.sub_field,
        example="ips",
        description=f"sub field of {KeyNames.field!r} key to use in filter",
        _priority=30,
    )
    value: Key = KeyBase(
        key=KeyNames.value,
        value_type=ValueTypes.field_value,
        example="192.168.1.24",
        description=f"value to filter on for {KeyNames.field!r} key",
        required=False,
        _priority=40,
        _lower=False,
    )
    section_name: Key = KeyBase(
        key=KeyNames.section_name, example="foobar", description="name of section",
    )
    section_type: Key = KeyChoices(
        key=KeyNames.section_type,
        example=Types.SIMPLE,
        description="type of section, controls which keys are used",
        choices=[x.default for x in Types.get_fields()],
        _priority=10,
    )
    operator: Key = KeyChoices(
        key=KeyNames.operator,
        example=Operators.exists.name,
        description=(
            f"operator to use for {KeyNames.field!r} key against "
            f"value in {KeyNames.value!r} key"
        ),
        choices=list(OperatorTypeMaps.get_map()),
        _priority=50,
    )
    not_flag: Key = KeyBoolean(
        key=KeyNames.not_flag,
        description=f"inverse matches of {KeyNames.operator!r} key",
        _priority=60,
    )
    bracket_expr: Key = KeyExpression(
        key=KeyNames.bracket_expr,
        example="simple1, or simple2, and complex1, complex2",
        description=(
            f"sections with {KeyNames.section_type!r} key of"
            f" {Types.COMPLEX_EXPR!r} or {Types.SIMPLE!r} to surround in brackets '()'"
        ),
        reference_types=[Types.SIMPLE, Types.COMPLEX_EXPR],
        value_type=ValueTypes.bracket_expr,
        _priority=70,
    )
    complex_expr: Key = KeyExpression(
        key=KeyNames.complex_expr,
        example="complex1, complex2",
        description=(
            f"sections with {KeyNames.section_type!r} key of"
            f" {Types.COMPLEX!r} to combine"
        ),
        reference_types=[Types.SIMPLE, Types.COMPLEX],
        value_type=ValueTypes.complex_expr,
        _priority=80,
    )


class Section(BaseData):
    @classmethod
    def new(cls, name: Types, keys: List[Key]) -> "Section":
        return dataclasses.make_dataclass(
            name, fields=[(x.key, Key, x) for x in keys], bases=(cls,),
        )


Simple: Section = Section.new(
    name=Types.SIMPLE,
    keys=[Keys.section_type, Keys.operator, Keys.value, Keys.field, Keys.not_flag],
)

Complex: Section = Section.new(
    name=Types.COMPLEX,
    keys=[Keys.section_type, Keys.operator, Keys.value, Keys.field, Keys.sub_field],
)

ComplexExpr: Section = Section.new(
    name=Types.COMPLEX_EXPR, keys=[Keys.section_type, Keys.complex_expr, Keys.not_flag],
)

BracketExpr: Section = Section.new(
    name=Types.BRACKET_EXPR, keys=[Keys.section_type, Keys.bracket_expr],
)

Sections = dataclasses.make_dataclass(
    "Sections",
    fields=[
        (x.__name__, Section, x) for x in [Simple, Complex, ComplexExpr, BracketExpr]
    ],
)


EXTERNAL_REFS: List[str] = [Types.BRACKET_EXPR, Types.SIMPLE, Types.COMPLEX_EXPR]
