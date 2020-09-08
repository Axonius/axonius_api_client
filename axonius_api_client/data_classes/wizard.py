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
    _entries: [Optional[List[dict]]] = dataclasses.field(default_factory=list)
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
    BRACKET_LEFT: str = "({query}"
    BRACKET_RIGHT: str = "{query})"
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
    example: str = ""


@dataclasses.dataclass
class EntryKeys(BaseData):
    TYPE: EntryKey = EntryKey(
        name="type",
        default=TypeNames.SIMPLE,
        choices=TypeNames.get_values(),
        description="Type of entry",
        example=f'"{TypeNames.SIMPLE}"',
    )
    SQ_NAME: EntryKey = EntryKey(
        name="name",
        required=True,
        description="Name",
        example='"All devices with old versions of Google Chrome"',
    )
    SQ_FIELDS: EntryKey = EntryKey(
        name="fields",
        description="Comma seperated list of fields",
        value_type="csv",
        example='"hostname,aws:aws_device_type,os.type"',
    )
    SQ_FIELDS_DEFAULT: EntryKey = EntryKey(
        name="fields_default",
        description="Include the default fields defined in the API client",
        default=True,
        value_type="bool",
        example='"y"',
    )
    SQ_TAGS: EntryKey = EntryKey(
        name="tags",
        description="Comma separated list of tags",
        default="",
        value_type="csv",
        example='"tag1,tag2"',
    )
    SQ_DESC: EntryKey = EntryKey(
        name="description",
        description="Description",
        example='"Find out dated software"',
    )
    FIELD_SIMPLE: EntryKey = EntryKey(
        name="field",
        required=True,
        description="Title/name of field",
        example='"hostname"',
    )
    FIELD_COMPLEX: EntryKey = EntryKey(
        name="field",
        required=True,
        description="Title/name of complex field",
        example='"installed_software"',
    )
    FIELD_COMPLEX_SUB: EntryKey = EntryKey(
        name="field",
        required=True,
        description="Title/name of sub-field of previous complex field entry",
        example='"version"',
    )
    OP: EntryKey = EntryKey(
        name="operator",
        description="Comparison operator, valid choices depend on field type",
        default="equals",
        example='"contains"',
    )
    OP_SUB: EntryKey = EntryKey(
        name="operator",
        description="Comparison operator, valid choices depend on sub-field type",
        default="equals",
        example='"less_than"',
    )
    VALUE_SIMPLE: EntryKey = EntryKey(
        name="value",
        description="Value to compare against field",
        value_type="variable",
        default="",
        example='"test.domain"',
    )
    VALUE_COMPLEX_SUB: EntryKey = EntryKey(
        name="value",
        description="Value to compare against complex sub field",
        value_type="variable",
        default="",
        example='"99"',
    )
    OR: EntryKey = EntryKey(
        name="or",
        default=False,
        description="Use or instead of and",
        value_type="bool",
        example="False",
    )
    NOT: EntryKey = EntryKey(
        name="not",
        default=False,
        description="Use not",
        value_type="bool",
        example="False",
    )
    BRACKET_LEFT: EntryKey = EntryKey(
        name="bracket_left",
        default=False,
        description="Open a bracket '(' ",
        value_type="bool",
        example="False",
    )
    BRACKET_RIGHT: EntryKey = EntryKey(
        name="bracket_right",
        default=False,
        description="Close a bracket ')'",
        value_type="bool",
        example="False",
    )


@dataclasses.dataclass
class EntryType(BaseData):
    name: str
    keys: List[EntryKey]


@dataclasses.dataclass
class AllEntryTypes(BaseData):
    SAVED_QUERY: EntryType = EntryType(
        name=TypeNames.SAVED_QUERY,
        keys=[
            EntryKeys.TYPE,
            EntryKeys.SQ_NAME,
            EntryKeys.SQ_DESC,
            EntryKeys.SQ_TAGS,
            EntryKeys.SQ_FIELDS,
            EntryKeys.SQ_FIELDS_DEFAULT,
        ],
    )
    SIMPLE: EntryType = EntryType(
        name=TypeNames.SIMPLE,
        keys=[
            EntryKeys.TYPE,
            EntryKeys.FIELD_SIMPLE,
            EntryKeys.OP,
            EntryKeys.VALUE_SIMPLE,
            EntryKeys.OR,
            EntryKeys.NOT,
            EntryKeys.BRACKET_LEFT,
            EntryKeys.BRACKET_RIGHT,
        ],
    )
    COMPLEX: EntryType = EntryType(
        name=TypeNames.COMPLEX,
        keys=[
            EntryKeys.TYPE,
            EntryKeys.FIELD_COMPLEX,
            EntryKeys.OR,
            EntryKeys.NOT,
            EntryKeys.BRACKET_LEFT,
            EntryKeys.BRACKET_RIGHT,
        ],
    )
    COMPLEX_SUB: EntryType = EntryType(
        name=TypeNames.COMPLEX_SUB,
        keys=[
            EntryKeys.TYPE,
            EntryKeys.FIELD_COMPLEX_SUB,
            EntryKeys.OP_SUB,
            EntryKeys.VALUE_COMPLEX_SUB,
        ],
    )


@dataclasses.dataclass
class EntryTypes(BaseData):
    SIMPLE: EntryType = AllEntryTypes.SIMPLE
    COMPLEX: EntryType = AllEntryTypes.COMPLEX


@dataclasses.dataclass
class TextEntryTypes(EntryTypes):
    SAVED_QUERY: EntryType = AllEntryTypes.SAVED_QUERY
    SIMPLE: EntryType = AllEntryTypes.SIMPLE
    COMPLEX: EntryType = AllEntryTypes.COMPLEX
    COMPLEX_SUB: EntryType = AllEntryTypes.COMPLEX_SUB


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
