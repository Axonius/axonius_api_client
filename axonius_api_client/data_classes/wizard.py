#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import dataclasses
from typing import List, Optional, Union

from .base import BaseData
from .fields import OperatorNameMaps


@dataclasses.dataclass
class Templates(BaseData):
    NOT: str = "not"
    AND: str = "and"
    OR: str = "or"
    OR_IDX0: str = ""
    LEFT_BRACKET: str = "({aql}"
    RIGHT_BRACKET: str = "{aql})"
    NOT_PRE: str = f"{NOT} {{aql}}"
    OR_PRE: str = f"{OR} {{aql}}"
    AND_PRE: str = f"{AND} {{aql}}"
    COMPLEX: str = "({field} == match([{aqls}]))"


class ExprKeys:
    TYPE: str = "type"
    SUBS: str = "subs"
    SRC: str = "source"
    IDX: str = "_idx"
    OP: str = "operator"
    SUBS: str = "subs"
    FIELD: str = "field"
    PVALUE: str = "parsed_value"
    EVALUE: str = "expr_value"
    AQL: str = "aql"
    VALUE: str = "value"
    EXPRS: str = "exprs"
    OR: str = "or"
    NOT: str = "not"
    EXPR_GUI: str = "expr_gui"
    BRACKET: str = "bracket"
    BRACKET_LEFT: str = "bracket_left"
    BRACKET_RIGHT: str = "bracket_right"
    BRACKET_WEIGHT: str = "bracket_weight"


class ExprGuiKeys:
    BRACKET_LEFT: str = "leftBracket"
    BRACKET_RIGHT: str = "rightBracket"
    BRACKET_WEIGHT: str = "bracketWeight"
    CHILDREN: str = "children"
    CONDITION: str = "condition"
    CONTEXT: str = "context"
    EXPR: str = "expression"
    FIELD: str = "field"
    FIELD_TYPE: str = "fieldType"
    FILTER: str = "filter"
    FILTER_ADAPTERS: str = "filteredAdapters"
    IDX: str = "i"
    NOT: str = "not"
    OP_COMP: str = "compOp"
    OP_LOGIC: str = "logicOp"
    VALUE: str = "value"
    CONTEXT_OBJ: str = "OBJ"


@dataclasses.dataclass
class ExprTypes(BaseData):
    SIMPLE: str = "simple"
    COMPLEX: str = "complex"
    BRACKET: str = "bracket"

    @classmethod
    def get_all_types(cls) -> List[str]:
        return cls.get_values()

    @classmethod
    def get_bracket_types(cls) -> List[str]:
        return [cls.COMPLEX, cls.SIMPLE]

    @classmethod
    def get_default_type(cls) -> str:
        return cls.SIMPLE


class ExprKeyDefaults:
    OP_VALUE: str = OperatorNameMaps.equals.name
    OP_NO_VALUE: str = OperatorNameMaps.exists.name
    OR: bool = False
    NOT: bool = False
    TYPE: str = ExprTypes.SIMPLE


@dataclasses.dataclass
class TextType(BaseData):
    name_text: str
    name_expr: str = ""


@dataclasses.dataclass
class TextTypes(BaseData):
    simple: TextType = TextType(name_text="simple", name_expr=ExprTypes.SIMPLE)
    start_complex: TextType = TextType(
        name_text="start_complex", name_expr=ExprTypes.COMPLEX,
    )
    stop_complex: TextType = TextType(name_text="stop_complex")
    start_bracket: TextType = TextType(
        name_text="start_bracket", name_expr=ExprTypes.BRACKET
    )
    stop_bracket: TextType = TextType(name_text="stop_bracket")


class GuiExpr:
    @classmethod
    def get(
        cls,
        aql: str,
        field: str,
        field_type: str,
        op_comp: str,
        not_flag: bool,
        or_flag: bool,
        idx: int,
        value: Optional[Union[str, int]],
        children: Optional[List[dict]] = None,
        filter_adapters: Optional[dict] = None,
        bracket_weight: int = 0,
        bracket_left: bool = False,
        bracket_right: bool = False,
    ) -> dict:
        children = children or [cls.get_child()]
        expr = {}
        expr[ExprGuiKeys.BRACKET_WEIGHT] = bracket_weight
        expr[ExprGuiKeys.CHILDREN] = children
        expr[ExprGuiKeys.OP_COMP] = op_comp
        expr[ExprGuiKeys.FIELD] = field
        expr[ExprGuiKeys.FIELD_TYPE] = field_type
        expr[ExprGuiKeys.FILTER] = aql
        expr[ExprGuiKeys.FILTER_ADAPTERS] = filter_adapters
        expr[ExprGuiKeys.BRACKET_LEFT] = bracket_left
        expr[ExprGuiKeys.OP_LOGIC] = cls.get_op_logic(or_flag=or_flag, idx=idx)
        expr[ExprGuiKeys.NOT] = not_flag
        expr[ExprGuiKeys.BRACKET_RIGHT] = bracket_right
        expr[ExprGuiKeys.VALUE] = value
        return expr

    @classmethod
    def get_complex(cls, children: List[dict], **kwargs) -> dict:
        kwargs["op_comp"] = ""
        kwargs["value"] = None
        expr = cls.get(children=children, **kwargs)
        expr[ExprGuiKeys.CONTEXT] = ExprGuiKeys.CONTEXT_OBJ
        return expr

    @classmethod
    def get_child(
        cls,
        aql: str = "",
        op_comp: str = "",
        field: str = "",
        filter_adapters: Optional[dict] = None,
        value: Optional[Union[int, str]] = None,
        idx: int = 0,
    ) -> dict:
        expr = {}
        expr[ExprGuiKeys.CONDITION] = aql
        expr[ExprGuiKeys.EXPR] = {}
        expr[ExprGuiKeys.EXPR][ExprGuiKeys.OP_COMP] = op_comp
        expr[ExprGuiKeys.EXPR][ExprGuiKeys.FIELD] = field
        expr[ExprGuiKeys.EXPR][ExprGuiKeys.FILTER_ADAPTERS] = filter_adapters
        expr[ExprGuiKeys.EXPR][ExprGuiKeys.VALUE] = value
        expr[ExprGuiKeys.IDX] = idx
        return expr

    @staticmethod
    def get_op_logic(or_flag: bool, idx: int) -> str:
        if idx:
            if or_flag:
                value = Templates.OR
            else:
                value = Templates.AND
        else:
            value = Templates.OR_IDX0
        return value

    @staticmethod
    def aql_add_logic(
        aql: str,
        or_flag: bool,
        not_flag: bool,
        idx: int,
        bracket: Optional[dict] = None,
    ) -> str:
        if aql:
            bracket = bracket or {}

            if bracket.get(ExprKeys.BRACKET_LEFT):
                aql = Templates.LEFT_BRACKET.format(aql=aql)

            if bracket.get(ExprKeys.BRACKET_RIGHT):
                aql = Templates.RIGHT_BRACKET.format(aql=aql)

            if not_flag:
                aql = Templates.NOT_PRE.format(aql=aql)

            if idx:
                if or_flag:
                    aql = Templates.OR_PRE.format(aql=aql)
                else:
                    aql = Templates.AND_PRE.format(aql=aql)

        return aql
