#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import dataclasses
from typing import List, Tuple, Union

from ..constants import NO, YES
from .base import BaseData
from .fields import Operators, OperatorTypeMaps


@dataclasses.dataclass
class ExprTypes(BaseData):
    SIMPLE: str = "simple"
    COMPLEX: str = "complex"
    BRACKET: str = "bracket"


class ExprKeys:
    TYPE: str = "type"
    SUBS: str = "subs"
    FROM: str = "from"
    SRC: str = "source"
    SRC_IDX: str = "index"
    SRC_LINE: str = "line"
    OP: str = "operator"
    SUBS: str = "subs"
    LOG: str = "logical"
    FIELD: str = "field"
    PVALUE: str = "parsed_value"
    EVALUE: str = "expr_value"
    AQL: str = "aql"


class ExprKeyDefaults:
    OP_VALUE: str = "equals"
    OP_NO_VALUE: str = "exists"
    LOG: str = "and"


@dataclasses.dataclass
class LogTypes(BaseData):
    AND: str = "and"
    OR: str = "or"
    AND_NOT: str = "and_not"
    OR_NOT: str = "or_not"


@dataclasses.dataclass
class TextTypes(BaseData):
    simple: str = ExprTypes.SIMPLE
    start_complex: str = ExprTypes.COMPLEX
    stop_complex: str = ""
    start_bracket: str = ExprTypes.BRACKET
    stop_bracket: str = ""


@dataclasses.dataclass
class Templates(BaseData):
    bracket_expr: str = "({aql_final})"
    complex_expr: str = "({field} == match([{aql_subs}]))"
    not_op: str = "not"
    and_op: str = "and"
    or_op: str = "or"
    invalid_choice: str = "Invalid choice {value!r}"
    missing_key: str = "Missing required key"


@dataclasses.dataclass
class Types(BaseData):
    SIMPLE: str = "simple_filter"
    COMPLEX: str = "complex_filter"
    COMPLEX_EXPR: str = "complex_expression"
    BRACKET_EXPR: str = "bracket_expression"
    EXPR: str = "expression"


@dataclasses.dataclass
class ValueTypes(BaseData):
    choice: str = "choice"
    complex_expr: str = "complex_expr"
    bracket_expr: str = "bracket_expr"
    expr: str = "expr"
    field: str = "field"
    sub_field: str = "sub_field"
    string: str = "string"
    field_value: str = "field_value"
    boolean: str = "boolean"


@dataclasses.dataclass
class KeyNames(BaseData):
    field: str = "field"
    value: str = "value"
    name: str = "name"
    type: str = "type"
    parent: str = "parent"
    operator: str = "operator"
    not_flag: str = "not_flag"
    or_flag: str = "or_flag"


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
    _split: str = ""
    _split_cnt: int = -1


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
    _split: str = ""
    _split_cnt: int = -1
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
    _split: str = ""
    _split_cnt: int = -1


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
    _split: str = ""
    _split_cnt: int = -1


@dataclasses.dataclass
class Keys(BaseData):
    field: Key = KeyBase(
        key=KeyNames.field,
        value_type=ValueTypes.field,
        example="agg:network_interfaces.ips",
        description="field (column) to use in filter",
        _priority=20,
    )
    sub_field: Key = KeyBase(
        key=KeyNames.field,
        value_type=ValueTypes.sub_field,
        example="agg:network_interfaces/ips",
        description="complex sub field to use in filter",
        _priority=20,
        _split="/",
        _split_cnt=2,
    )
    value: Key = KeyBase(
        key=KeyNames.value,
        value_type=ValueTypes.field_value,
        example="192.168.1.24",
        description=f"value to filter on for {KeyNames.field!r} key",
        required=False,
        _priority=100,
        _lower=False,
    )
    name: Key = KeyBase(
        key=KeyNames.name, example="foobar", description="name of section",
    )
    parent: Key = KeyBase(
        key=KeyNames.parent, example="foobar", description="parent of section",
    )
    type: Key = KeyChoices(
        key=KeyNames.type,
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
    or_flag: Key = KeyBoolean(
        key=KeyNames.or_flag,
        description="use OR instead of AND with the previous filter",
        _priority=60,
    )
    bracket_expr: Key = KeyExpression(
        key=KeyNames.value,
        example="simple1, simple2, complex_expr1",
        description="references to sections to surround in brackets '()'",
        reference_types=[Types.SIMPLE, Types.COMPLEX_EXPR],
        value_type=ValueTypes.bracket_expr,
        _priority=70,
    )
    complex_expr: Key = KeyExpression(
        key=KeyNames.value,
        example="complex1, complex2",
        description="references to sections to combine into a complex filter",
        reference_types=[Types.SIMPLE, Types.COMPLEX],
        value_type=ValueTypes.complex_expr,
        _priority=70,
    )
    expr: Key = KeyExpression(
        key=KeyNames.value,
        example="simple1, complex_expr1, bracket_expr1",
        description="references to sections to parse a complete query",
        reference_types=[Types.SIMPLE, Types.COMPLEX_EXPR, Types.BRACKET_EXPR],
        value_type=ValueTypes.expr,
        _priority=70,
    )


class Section(BaseData):
    @classmethod
    def new(cls, name: Types, keys: List[Key]) -> "Section":
        return dataclasses.make_dataclass(
            name, fields=[(x.key, Key, x) for x in keys], bases=(cls,),
        )


Simple: Section = Section.new(
    name=Types.SIMPLE,
    keys=[
        Keys.type,
        Keys.operator,
        Keys.value,
        Keys.field,
        Keys.not_flag,
        Keys.or_flag,
    ],
)

Complex: Section = Section.new(
    name=Types.COMPLEX, keys=[Keys.type, Keys.operator, Keys.value, Keys.sub_field],
)

ComplexExpr: Section = Section.new(
    name=Types.COMPLEX_EXPR,
    keys=[Keys.type, Keys.complex_expr, Keys.not_flag, Keys.or_flag],
)

BracketExpr: Section = Section.new(
    name=Types.BRACKET_EXPR, keys=[Keys.type, Keys.bracket_expr],
)

Expr: Section = Section.new(
    name=Types.EXPR, keys=[Keys.type, Keys.expr],
)

Sections = dataclasses.make_dataclass(
    "Sections",
    fields=[
        (x.__name__, Section, x)
        for x in [Simple, Complex, ComplexExpr, BracketExpr, Expr]
    ],
    bases=(BaseData,),
)
