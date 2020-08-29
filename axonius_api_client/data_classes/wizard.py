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
    # BRACKET: str = "({sub_aqls})"
    COMPLEX: str = "({field} == match([{sub_aqls}]))"


class ExprKeys:
    TYPE: str = "type"
    SUBS: str = "subs"
    SRC: str = "source"
    SRC_LINE_NUM: str = "line_number"
    SRC_LINE: str = "line"
    IDX: str = "_idx"
    OP: str = "operator"
    SUBS: str = "subs"
    FIELD: str = "field"
    PVALUE: str = "parsed_value"
    EVALUE: str = "expr_value"
    AQL: str = "aql"
    VALUE: str = "value"
    SUB: str = "sub_field"
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


class ExprKeyDefaults:
    OP_VALUE: str = OperatorNameMaps.equals.name
    OP_NO_VALUE: str = OperatorNameMaps.exists.name
    OR: bool = False
    NOT: bool = False


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
        op_comp: str,  # One of: value of data_classes.fields.OperatorNames
        value: Optional[Union[str, int]] = None,
        children: Optional[List[dict]] = None,
        filter_adapters: Optional[dict] = None,
        bracket_weight: int = 0,
        bracket_left: bool = False,
        bracket_right: bool = False,
        op_logic: str = "",  # One of: "", "and", "or"
        not_flag: bool = False,
    ) -> dict:
        children = children or [cls.get_child()]
        cls.set_idx(exprs=children)
        expr = {}
        expr[ExprGuiKeys.BRACKET_WEIGHT] = bracket_weight
        expr[ExprGuiKeys.CHILDREN] = children
        expr[ExprGuiKeys.OP_COMP] = op_comp
        expr[ExprGuiKeys.FIELD] = field
        expr[ExprGuiKeys.FIELD_TYPE] = field_type
        expr[ExprGuiKeys.FILTER] = aql
        expr[ExprGuiKeys.FILTER_ADAPTERS] = filter_adapters
        expr[ExprGuiKeys.BRACKET_LEFT] = bracket_left
        expr[ExprGuiKeys.OP_LOGIC] = op_logic
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
        **kwargs,
    ) -> dict:
        expr = {}
        expr[ExprGuiKeys.CONDITION] = aql
        expr[ExprGuiKeys.EXPR] = {}
        expr[ExprGuiKeys.EXPR][ExprGuiKeys.OP_COMP] = op_comp
        expr[ExprGuiKeys.EXPR][ExprGuiKeys.FIELD] = field
        expr[ExprGuiKeys.EXPR][ExprGuiKeys.FILTER_ADAPTERS] = filter_adapters
        expr[ExprGuiKeys.EXPR][ExprGuiKeys.VALUE] = value
        expr[ExprGuiKeys.IDX] = 0
        return expr

    @classmethod
    def set_idx(cls, exprs: List[dict], first: bool = True):
        idx = 0
        for expr in exprs:
            if not first and not idx:
                expr.pop(ExprGuiKeys.IDX, None)
                idx += 1
                continue

            expr[ExprGuiKeys.IDX] = idx
            idx += 1
