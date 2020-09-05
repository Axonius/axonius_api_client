#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import dataclasses
from typing import List, Optional, Union

from .base import BaseData


@dataclasses.dataclass
class SavedQuery(BaseData):
    expressions: List[dict] = dataclasses.field(default_factory=list)
    query: List[str] = dataclasses.field(default_factory=list)
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    fields_manual: Optional[List[str]] = None

    # def to_dict(self) -> dict:
    #     value = dataclasses.asdict(self)

    #     value["query"] = " ".join([x for x in value["query"] or [] if x.strip()])

    #     found_left = False
    #     found_right = False

    #     for idx, expr in enumerate(value["expressions"] or []):
    #         expr[ExprKeys.IDX] = idx

    #         if expr[ExprKeys.BRACKET_LEFT]:
    #             found_left = True

    #         if expr[ExprKeys.BRACKET_RIGHT]:
    #             found_right = True

    #         for idx_child, expr_child in enumerate(expr[ExprKeys.CHILDREN]):
    #             expr_child[ExprKeys.IDX] = idx_child

    #     if found_left and not found_right:
    #         expr = value["expressions"][-1]
    #         expr[ExprKeys.BRACKET_RIGHT] = True
    #         expr[ExprKeys.FILTER] += ")"
    #         value["query"] += ")"

    #     return {k: v for k, v in value.items() if v not in [None, [], ""]}


@dataclasses.dataclass
class TypeNames(BaseData):
    SIMPLE: str = "simple"
    COMPLEX: str = "complex"
    COMPLEX_SUB: str = "complex_sub"
    SAVED_QUERY: str = "saved_query"


@dataclasses.dataclass
class Templates(BaseData):
    NOT: str = "not"
    AND: str = "and"
    OR: str = "or"
    OP_LOGIC_AND: str = AND
    OP_LOGIC_OR: str = OR
    OP_LOGIC_IDX0: str = ""
    LEFT_BRACKET: str = "({query}"
    RIGHT_BRACKET: str = "{query})"
    NOT_PRE: str = f"{NOT} {{query}}"
    OR_PRE: str = f"{OR} {{query}}"
    AND_PRE: str = f"{AND} {{query}}"
    COMPLEX: str = "({field} == match([{sub_queries}]))"


@dataclasses.dataclass
class EntryKey(BaseData):
    name: str
    description: Union[str, dict]
    default: Optional[Union[str, int, bool, dict]] = None
    choices: Optional[List[str]] = None
    required: bool = False
    value_type: str = "str"


@dataclasses.dataclass
class EntryKeys(BaseData):
    TYPE: EntryKey = EntryKey(
        name="type",
        default=TypeNames.SIMPLE,
        choices=TypeNames.get_values(),
        description="Type of entry",
    )
    SQ_NAME: EntryKey = EntryKey(
        name="name", required=True, description="Name of Saved Query",
    )
    SQ_FIELDS: EntryKey = EntryKey(
        name="fields",
        required=True,
        description="List of fields to include in Saved Query",
        value_type="csv",
    )
    SQ_TAGS: EntryKey = EntryKey(
        name="tags",
        description="List of tags for Saved Query",
        default="",
        value_type="csv",
    )
    SQ_DESC: EntryKey = EntryKey(
        name="description", description="Description of Saved Query"
    )
    FIELD: EntryKey = EntryKey(
        name="field",
        required=True,
        description={
            TypeNames.SIMPLE: "Title/name of field",
            TypeNames.COMPLEX: "Title/name of complex field",
            TypeNames.COMPLEX_SUB: (
                "Title/name of sub-field of previous complex field entry"
            ),
        },
    )
    OP: EntryKey = EntryKey(
        name="operator",
        description="Comparison operator, valid choices depend on field type",
        default="equals",
    )
    VALUE: EntryKey = EntryKey(
        name="value",
        description={
            TypeNames.SIMPLE: "Value to compare against field",
            TypeNames.COMPLEX_SUB: "Value to compare against complex sub field",
            TypeNames.SAVED_QUERY: "Description of Saved Suery",
        },
        value_type="variable",
    )
    BRACKET: EntryKey = EntryKey(
        name="bracket",
        default="",
        description="Set the left or right bracket",
        choices=["", "left", "right"],
    )
    LOGIC: EntryKey = EntryKey(
        name="logic",
        default="and",
        description="Set the and/or/not logic",
        choices=["and", "and not", "or", "or not"],
    )


@dataclasses.dataclass
class EntryType(BaseData):
    name: str
    keys: List[EntryKey]


@dataclasses.dataclass
class EntryTypes(BaseData):
    SIMPLE: EntryType = EntryType(
        name=TypeNames.SIMPLE,
        keys=[
            EntryKeys.TYPE,
            EntryKeys.FIELD,
            EntryKeys.OP,
            EntryKeys.VALUE,
            EntryKeys.LOGIC,
            EntryKeys.BRACKET,
        ],
    )
    COMPLEX: EntryType = EntryType(
        name=TypeNames.COMPLEX,
        keys=[EntryKeys.TYPE, EntryKeys.FIELD, EntryKeys.LOGIC, EntryKeys.BRACKET],
    )
    COMPLEX_SUB: EntryType = EntryType(
        name=TypeNames.COMPLEX_SUB,
        keys=[EntryKeys.TYPE, EntryKeys.FIELD, EntryKeys.OP, EntryKeys.VALUE],
    )
    SAVED_QUERY: EntryType = EntryType(
        name=TypeNames.SAVED_QUERY,
        keys=[
            EntryKeys.TYPE,
            EntryKeys.SQ_NAME,
            EntryKeys.SQ_DESC,
            EntryKeys.SQ_TAGS,
            EntryKeys.SQ_FIELDS,
        ],
    )


# XXX CsvKeys


class ExprKeys:
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
