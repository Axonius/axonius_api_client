#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import dataclasses
from typing import Any, List, Optional, Union

from ..data import BaseData


class Consts:
    SRC: str = "source"
    IN_COMPLEX: str = "in_complex"
    ENTRIES: str = "entries"
    QUERY: str = "query"
    EXPRS: str = "expressions"
    SUBS: str = "subs"
    WEIGHT: str = "bracket_weight"

    SQ: str = "sq"
    SQ_NAME: str = "name"
    FNAME: str = "name"
    FEXPR: str = "expr_field_type"
    FANAME: str = "adapter_name"
    FSUBS: str = "sub_fields"
    FDETAILS: str = "_details"
    FCOMPLEX: str = "is_complex"
    TYPE_STR: str = "str"
    TYPE_CSV: str = "csv"
    FMANUAL: str = "fields_manual"
    FDEFAULT: str = "fields_default"
    NO_FDEFAULT: str = "no_fields_default"

    CLI_SRC_STR: str = "Command Line Interface"
    CSV_SRC_STR: str = "csv text string"
    CSV_SRC_PATH: str = "csv file {path}"
    TXT_SRC_STR: str = "text string"
    TXT_SRC_PATH: str = "text file {path}"

    ITEM_SEP: str = " "
    VALUE_SEP: str = "="
    WORDCHARS: str = ""  # f"{VALUE_SEP}"

    NOT: str = "not"
    AND: str = "and"
    OR: str = "or"

    OP_LOGIC_AND: str = AND
    OP_LOGIC_OR: str = OR
    OP_LOGIC_IDX0: str = ""

    LEFT_TMPL: str = "({query}"
    RIGHT_TMPL: str = "{query})"
    NOT_TMPL: str = f"{NOT} {{query}}"
    OR_TMPL: str = f"{OR} {{query}}"
    AND_TMPL: str = f"{AND} {{query}}"
    COMPLEX_TMPL: str = "({field} == match([{sub_queries}]))"
    LEFTB: str = "bracket_left"
    RIGHTB: str = "bracket_right"

    DESC: str = "DESCRIPTION"
    REQ: str = "REQUIRED"
    OPT: str = "OPTIONAL"
    DEFAULT: str = "DEFAULT"
    CHOICES: str = "CHOICES"
    STR_EXAMPLE: str = "# EXAMPLE:"
    STR_EXAMPLES: str = "# EXAMPLES:"

    FLAGS_FIELD: dict = {
        OR: "Use or instead of and",
        NOT: "Use not",
        LEFTB: "Open a bracket '('",
        RIGHTB: "Close a bracket ')'",
    }
    FLAGS_SQ = {
        NO_FDEFAULT: (
            "Do not include the default columns from the API client in the Saved Query"
        ),
    }


@dataclasses.dataclass
class TypeNames(BaseData):
    SIMPLE: str = "simple"
    COMPLEX: str = "complex"
    COMPLEX_SUB: str = "complex_sub"
    SAVED_QUERY: str = "saved_query"


@dataclasses.dataclass
class EntryKey(BaseData):
    name: str
    description: Union[str, dict]
    example: str
    value_type: str
    required: bool
    default: Optional[Union[str, int, bool, dict]] = None
    choices: Optional[List[str]] = None


@dataclasses.dataclass
class EntryKeys(BaseData):
    TYPE: EntryKey = EntryKey(
        name="type",
        required=True,
        choices=TypeNames.get_values(),
        description="Type of entry",
        example={x: x for x in TypeNames.get_values()},
        value_type=Consts.TYPE_STR,
    )
    SQ_FIELDS: EntryKey = EntryKey(
        name="fields",
        required=False,
        default="default",
        description="Comma seperated list of columns to display in the Saved Query",
        value_type=Consts.TYPE_CSV,
        example="aws:aws_device_type,os.type",
    )
    SQ_TAGS: EntryKey = EntryKey(
        name="tags",
        required=False,
        description="Comma separated list of tags to set on the Saved Query",
        default="",
        value_type=Consts.TYPE_CSV,
        example="tag1,tag2",
    )
    SQ_DESC: EntryKey = EntryKey(
        name="description",
        required=False,
        description="Description of the Saved Query",
        default="",
        value_type=Consts.TYPE_STR,
        example="Find outdated browsers",
    )
    VALUE: EntryKey = EntryKey(
        name="value",
        required=True,
        description={
            TypeNames.SAVED_QUERY: "Name of saved question",
            TypeNames.SIMPLE: "{field name} {operator} {value}",
            TypeNames.COMPLEX: "Name of complex field",
            TypeNames.COMPLEX_SUB: "{complex sub field name} {operator} {value}",
        },
        value_type=Consts.TYPE_STR,
        example={
            TypeNames.SAVED_QUERY: "Old browsers",
            TypeNames.SIMPLE: "hostname contains test",
            TypeNames.COMPLEX: "installed_software",
            TypeNames.COMPLEX_SUB: "version less_than 99",
        },
    )
    FLAGS: EntryKey = EntryKey(
        name="flags",
        required=False,
        description={
            TypeNames.SAVED_QUERY: Consts.FLAGS_SQ,
            TypeNames.SIMPLE: Consts.FLAGS_FIELD,
            TypeNames.COMPLEX: Consts.FLAGS_FIELD,
        },
        choices={
            TypeNames.SAVED_QUERY: list(Consts.FLAGS_SQ),
            TypeNames.SIMPLE: list(Consts.FLAGS_FIELD),
            TypeNames.COMPLEX: list(Consts.FLAGS_FIELD),
        },
        value_type=Consts.TYPE_CSV,
        default={
            TypeNames.SAVED_QUERY: Consts.NO_FDEFAULT,
            TypeNames.SIMPLE: "",
            TypeNames.COMPLEX: "",
        },
        example={
            TypeNames.SAVED_QUERY: ", ".join(list(Consts.FLAGS_SQ)),
            TypeNames.SIMPLE: ", ".join(list(Consts.FLAGS_FIELD)),
            TypeNames.COMPLEX: ", ".join(list(Consts.FLAGS_FIELD)),
        },
    )


@dataclasses.dataclass
class EntryType(BaseData):
    name: str
    keys: List[EntryKey]

    @staticmethod
    def key_dict(value: Any, entry_type: "EntryType") -> Any:
        if isinstance(value, dict):
            return value[entry_type.name]
        return value


@dataclasses.dataclass
class AllEntryTypes(BaseData):
    SAVED_QUERY: EntryType = EntryType(
        name=TypeNames.SAVED_QUERY,
        keys=[
            EntryKeys.TYPE,
            EntryKeys.VALUE,
            EntryKeys.SQ_DESC,
            EntryKeys.SQ_TAGS,
            EntryKeys.SQ_FIELDS,
        ],
    )
    SIMPLE: EntryType = EntryType(
        name=TypeNames.SIMPLE, keys=[EntryKeys.TYPE, EntryKeys.VALUE, EntryKeys.FLAGS],
    )
    COMPLEX: EntryType = EntryType(
        name=TypeNames.COMPLEX, keys=[EntryKeys.TYPE, EntryKeys.VALUE, EntryKeys.FLAGS],
    )
    COMPLEX_SUB: EntryType = EntryType(
        name=TypeNames.COMPLEX_SUB, keys=[EntryKeys.TYPE, EntryKeys.VALUE],
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
