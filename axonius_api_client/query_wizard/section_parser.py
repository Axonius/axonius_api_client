#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import logging
from typing import Any, List, Optional, Union

from ..constants import LOG_LEVEL_WIZARD
from ..data_classes.fields import CUSTOM_FIELDS_MAP
from ..data_classes.wizard import Key, Keys, Section, Sections, Templates
from ..exceptions import AxonError, SectionParserKeyError, WizardError
from ..logs import get_obj_log
from ..tools import check_empty, check_type, coerce_bool
from .value_parser import ValueParser


class SectionParser:
    def __init__(
        self, wizard, log_level=LOG_LEVEL_WIZARD,
    ):
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        """Logger for this object."""
        self.wizard = wizard

    def __call__(self, name: str, section: dict, parent: str = "", idx: int = 0) -> dict:
        self.LOG.debug(f"Now parsing section {name!r}")
        self.parent = parent
        self.idx = idx
        self.parsed: dict = {}
        self.parsed[Keys.name.key] = name

        self.unparsed: dict = section
        self.name: str = name
        self.type: str = self.get(key=Keys.type)
        self.section: Section = getattr(Sections, self.type)
        self.keys: List[Key] = sorted(
            [x.default for x in self.section.get_fields()], key=lambda x: x._priority,
        )

        for key in self.keys:
            try:
                self.parsed[key.key] = self.get(key=key)
            except SectionParserKeyError:
                raise
            except AxonError as exc:
                raise SectionParserKeyError(parser=self, key=key, msg=str(exc))

        return self.parsed

    def get(self, key: Key):
        if key.key in self.parsed:
            return self.parsed[key.key]

        value = self.unparsed.get(key.key, key.default)

        if key.required:
            if key.key not in self.unparsed:
                raise SectionParserKeyError(
                    parser=self, key=key, msg=Templates.missing_key
                )

        if isinstance(value, str):
            if key._lower:
                value = value.lower()

            if key._strip:
                value = value.strip()

        handler = f"handle_{key.value_type}"
        handler_method = getattr(self, handler, None)

        if handler_method:
            value = handler_method(value=value, key=key)
        else:
            raise WizardError(f"Handler {handler!r} not found for key:\n{key.to_dict()}")

        return value

    def handle_string(self, value: str, key: Key) -> str:
        check_type(value=value, exp=str)

        if key.required:
            check_empty(value=value)

        if key._split:
            if key._split not in value:
                msg = f"Missing {key._split!r} in {value!r}, example: {key.example}"
                raise WizardError(msg)

            split = [x.strip() for x in value.split(key._split, key._split_cnt)]

            if not all(split):
                msg = f"Empty values in {split} after {value!r} split on {key._split!r}"
                raise WizardError(msg)

            return split

        return value

    def handle_choice(self, value: str, key: Key) -> str:
        value = self.handle_string(value=value, key=key)
        if value not in key.choices:
            raise SectionParserKeyError(
                parser=self, key=key, msg=Templates.invalid_choice.format(value=value),
            )
        return value

    def handle_boolean(self, value: Union[str, bool, int], key: Key) -> bool:
        return coerce_bool(obj=value)

    def handle_field(self, value: str, key: Key):
        value = self.handle_string(value=value, key=key)
        value = self.wizard.apiobj.fields.get_field_name(
            value=value,
            fields_map=self.wizard._fields_map,
            key=None,
            custom_fields_map=CUSTOM_FIELDS_MAP,
        )
        return value

    def handle_sub_field(self, value: str, key: Key):
        name, sub_name = self.handle_string(value=value, key=key)

        field = self.wizard.apiobj.fields.get_field_name(
            value=name,
            fields_map=self.wizard._fields_map,
            key=None,
            custom_fields_map=CUSTOM_FIELDS_MAP,
        )

        adapter = field["adapter_name"]
        field_name = field["name"]
        sub_fields = {x["name"]: x for x in field["sub_fields"]}

        if not field["is_complex"]:
            schemas = [
                x
                for x in self.wizard._fields_map[adapter]
                if x["is_complex"] and x["name"] != "all"
            ]
            msg = [
                f"Invalid complex field {field_name!r}",
                f"Valid complex fields for {adapter}:",
                *self.wizard.apiobj.fields._prettify_schemas(schemas=schemas),
            ]
            msg = "\n".join(msg)
            raise SectionParserKeyError(parser=self, key=key, msg=msg)

        if sub_name not in sub_fields:
            valids = "\n  - " + "\n  - ".join(sub_fields)
            msg = [
                f"Invalid sub field {sub_name!r} for field {field_name!r}",
                f"Valid sub fields:{valids}",
            ]
            msg = "\n".join(msg)
            raise SectionParserKeyError(parser=self, key=key, msg=msg)

        return sub_fields[sub_name]

    def handle_field_value(self, value: str, key: Key):
        operator = self.get(key=Keys.operator)
        field = self.get(key=Keys.field)
        parser = ValueParser(
            value=value, operator=operator, apiobj=self.wizard.apiobj, field=field,
        )
        parsed = parser()
        return parsed

    def handle_complex_expr(self, value: Union[List[str], str], key: Key) -> dict:
        sections = self.parse_expr(value=value, key=key)

        not_flag = self.get(key=Keys.not_flag)
        or_flag = self.get(key=Keys.or_flag)

        aql_subs = ""

        complex_field = ""
        field_type = ""
        names = []
        exprs = []

        for section in sections:
            name = section[Keys.name.key]
            value = section[Keys.value.key]
            sq_expr = value["sq_expr"]
            aql_sub = value["aql"]

            exprs.append(get_expr_child(aql=aql_sub, **sq_expr))

            sub_field = section[Keys.sub_field.key]
            field_parent = sub_field["parent"]
            field_type = sub_field["expr_field_type"]

            if complex_field and field_parent != complex_field:
                names = ", ".join(names)
                msg = (
                    f"Field {field_parent!r} in section {name!r} must match "
                    f"field {complex_field!r} used in sections: {names}"
                )
                raise WizardError(msg)

            complex_field = field_parent
            names.append(name)

            if aql_subs:
                aql_sub = f"{Templates.and_op} {aql_sub}"

            aql_subs += aql_sub

        tmpl = Templates.complex_expr.format
        aql = tmpl(field=complex_field, aql_subs=aql_subs).strip()
        aql, logic_op = add_pre_aql(
            aql=aql, or_flag=or_flag, not_flag=not_flag, parent=self.parent, idx=self.idx
        )

        expr = get_expr_complex(
            aql=aql,
            field=complex_field,
            field_type=field_type,
            children=exprs,
            logic_op=logic_op,
            not_flag=not_flag,
        )

        self.LOG.info(f"Complex AQL produced: {aql}")
        return {"aql": aql, "parent": self.parent, "expr": expr, "idx": self.idx}

    def handle_bracket_expr(self, value: Union[List[str], str], key: Key) -> dict:
        section_names = self.parse_expr(value=value, key=key)
        aql_final = ""

        for section_name in section_names:
            section = self.wizard.parsed[section_name]
            aql = section[Keys.value.key]["aql"].strip()
            not_flag = section.get(Keys.not_flag.key, False)
            or_flag = section.get(Keys.or_flag.key, False)

            if not_flag and not aql.startswith(Templates.not_text):
                aql = Templates.not_text + aql

            if aql_final:
                if or_flag:
                    aql = Templates.or_text + aql
                else:
                    aql = Templates.and_text + aql

            aql_final += aql

        tmpl = Templates.bracket_expr.format
        aql_final = tmpl(aql_final=aql_final)
        self.LOG.info(f"Bracketed AQL produced: {aql_final}")
        return {"aql": aql_final, "sections": section_names}

    def handle_expr(self, value: Union[List[str], str], key: Key) -> dict:
        sections = self.parse_expr(value=value, key=key)
        aql = ""

        for section in sections:
            aql_sub = section[Keys.value.key]["aql"].strip()
            if aql and not aql_sub.startswith(" "):
                aql_sub = f" {aql_sub}"
            # not_flag = section.get(Keys.not_flag.key, False)
            # or_flag = section.get(Keys.or_flag.key, False)
            # section_aql, logic_op = self.add_p
            # if not_flag and not aql.startswith(Templates.not_text):
            #     aql = Templates.not_text + aql

            # if aql_final:
            #     if or_flag:
            #         aql = Templates.or_text + aql
            #     else:
            #         aql = Templates.and_text + aql

            aql += aql_sub

        self.LOG.info(f"AQL produced: {aql}")
        return {"aql": aql}

    def parse_expr(self, value: List[str], key: Key) -> List[dict]:
        if isinstance(value, str):
            value = [x.strip() for x in value.split(",") if x.strip()]

        check_type(value=value, exp=list, exp_items=str)
        check_empty(value=value)
        sections = []
        for idx, item in enumerate(value):
            if item == self.name:
                raise WizardError(f"Invalid reference to own section name: {item!r}")

            section = self.wizard.parse(name=item, parent=self.name, idx=idx)
            sections.append(section)
            item_type = section[Keys.type.key]

            if item_type not in key.reference_types:
                valid = "\n - " + "\n - ".join(key.reference_types)
                msg = (
                    f"Invalid reference to section {item!r} of type {item_type!r}, "
                    f"valid reference types:{valid}"
                )
                raise WizardError(msg)

        return sections


def get_expr_child(
    aql: str = "",
    operator: str = "",
    field: str = "",
    value: Optional[Any] = None,
    **kwargs,
):
    return {
        "condition": aql,
        "expression": {
            "compOp": operator,
            "field": field,
            "filteredAdapters": None,
            "value": value,
        },
        "i": 0,
    }


def set_expr_idx(exprs):
    idx = 0
    for expr in exprs:
        expr["i"] = idx
        idx += 1


def get_expr(
    aql: str,
    field: str,
    field_type: str,
    value: Any,
    operator: str,
    children: List[dict] = None,
    idx: int = 0,
    bracket_weight: int = 0,
    bracket_left: bool = False,
    bracket_right: bool = False,
    logic_op: str = "",
    not_flag: bool = False,
):
    children = children or [get_expr_child()]
    set_expr_idx(exprs=children)
    return {
        "bracketWeight": bracket_weight,
        "children": children,
        "compOp": operator,
        "field": field,
        "fieldType": field_type,
        "filter": aql,
        "i": idx,
        "leftBracket": bracket_left,
        "logicOp": logic_op,
        "not": not_flag,
        "rightBracket": bracket_right,
        "value": value,
    }


def get_expr_complex(
    aql: str,
    field: str,
    field_type: str,
    children: List[dict],
    idx: int = 0,
    bracket_weight: int = 0,
    bracket_left: bool = False,
    bracket_right: bool = False,
    logic_op: str = "",
    not_flag: bool = False,
):
    set_expr_idx(exprs=children)
    return {
        "bracketWeight": bracket_weight,
        "children": children,
        "compOp": "",
        "context": "OBJ",
        "field": field,
        "fieldType": field_type,
        "filter": aql,
        "i": idx,
        "leftBracket": bracket_left,
        "logicOp": logic_op,
        "not": not_flag,
        "rightBracket": bracket_right,
        "value": None,
    }


def add_pre_aql(aql: str, or_flag: bool, not_flag: bool, parent: str, idx: int):
    logic_op = ""

    if parent and idx:
        if or_flag:
            logic_op = Templates.or_op
        else:
            logic_op = Templates.and_op

    if not_flag and not aql.startswith(Templates.not_op):
        aql = f"{Templates.not_op} {aql}"

    if logic_op:
        aql = f"{logic_op} {aql}"

    return aql, logic_op
