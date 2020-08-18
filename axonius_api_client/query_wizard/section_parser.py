#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import logging
from typing import List, Union

from ..constants import LOG_LEVEL_WIZARD
from ..data_classes.fields import CUSTOM_FIELDS_MAP
from ..data_classes.wizard import (ErrorTemplates, ExprTemplates, Key, Keys,
                                   Section, Sections, Types)
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

    def __call__(self, name: str, section: dict) -> dict:
        self.LOG.debug(f"Now parsing section {name!r}")

        self.parsed: dict = {}
        self.parsed[Keys.section_name.key] = name

        self.unparsed: dict = section
        self.name: str = name
        self.type: str = self.get(key=Keys.section_type)
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
                    parser=self, key=key, msg=ErrorTemplates.missing_key
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
            raise WizardError(f"No handler for {key.value_type}")

        return value

    def _check_empty(self, value: str, key: Key):
        if key.required:
            check_empty(value=value)

    def handle_string(self, value: str, key: Key) -> str:
        check_type(value=value, exp=str)

        if key.required:
            check_empty(value=value)

        return value

    def handle_choice(self, value: str, key: Key) -> str:
        value = self.handle_string(value=value, key=key)
        if value not in key.choices:
            raise SectionParserKeyError(
                parser=self,
                key=key,
                msg=ErrorTemplates.invalid_choice.format(value=value),
            )
        return value

    def handle_boolean(self, value: Union[str, bool, int], key: Key) -> bool:
        return coerce_bool(obj=value)

    def handle_complex_expression(self, value: Union[List[str], str], key: Key) -> dict:
        exprs = self.wizard._parse_expression(
            value=value, parent_name=self.name, reference_types=key.reference_types
        )

        not_flag = self.get(key=Keys.not_flag)
        aqls = ""

        field = ""
        names = []

        for expr in exprs:
            name = expr["name"]
            section = self.wizard.parsed[name]
            section_aql = section["aql"]
            section_field = section[Keys.field.key]["name"]

            if field and section_field != field:
                names = ", ".join(names)
                msg = (
                    f"Field {section_field!r} in section {name!r} must match "
                    f"field {field!r} used in sections: {names}"
                )
                raise WizardError(msg)

            field = section_field
            names.append(name)

            if aqls:
                section_aql = ExprTemplates.and_text + section_aql

            aqls += section_aql

        aql = ExprTemplates.complex_expr.format(field=field, aqls=aqls).strip()

        if not_flag:
            aql = ExprTemplates.not_text + aql

        self.LOG.info(f"Complex AQL produced: {aql}")
        self.parsed["aql"] = aql
        return {"aql": aql, "sections": exprs}

    def handle_bracket_expression(self, value: Union[List[str], str], key: Key) -> dict:
        parsed = self.wizard.parse_expression(
            value=value, parent_name=self.name, reference_types=key.reference_types
        )
        aql = ExprTemplates.bracket_expr.format(aqls=parsed["aql"])
        self.LOG.info(f"Bracketed AQL produced: {aql}")
        self.parsed["aql"] = parsed["aql"] = aql
        return parsed

    def handle_field(self, value: str, key: Key):
        value = self.handle_string(value=value, key=key)
        value = self.wizard.apiobj.fields.get_field_name(
            value=value,
            fields_map=self.wizard._fields_map,
            key=None,
            custom_fields_map=CUSTOM_FIELDS_MAP,
        )
        return value

    def handle_complex_field(self, value: str, key: Key):
        value = self.handle_string(value=value, key=key)
        value = self.wizard.apiobj.fields.get_field_name(
            value=value, fields_map=self.wizard._fields_map, key=None
        )
        return value

    def handle_sub_field(self, value: str, key: Key):
        value = self.handle_string(value=value, key=key)
        field = self.get(key=Keys.field)

        adapter = field["adapter_name"]
        name = field["name"]
        sub_fields = {x["name"]: x for x in field["sub_fields"]}

        if not field["is_complex"]:
            fields = self.wizard._fields_map[adapter]
            schemas = [x for x in fields if x["is_complex"] and x["name"] != "all"]
            valids = "\n".join(
                self.wizard.apiobj.fields._prettify_schemas(schemas=schemas)
            )
            msg = [
                f"Field {name!r} is not a complex field",
                f"Valid complex fields for {adapter}:",
                f"{valids}",
            ]
            raise SectionParserKeyError(parser=self, key=key, msg="\n".join(msg))

        if value not in sub_fields:
            valids = "\n  - " + "\n  - ".join(sub_fields)
            msg = [
                f"Sub field {value!r} is not a valid sub field of field {name!r}",
                f"Valid sub fields for field {name!r}:{valids}",
            ]
            raise SectionParserKeyError(parser=self, key=key, msg="\n".join(msg))

        return sub_fields[value]

    def handle_field_value(self, value: str, key: Key):
        section_type = self.get(key=Keys.section_type)

        if section_type == Types.COMPLEX:
            sub_field = self.get(key=Keys.sub_field)
        else:
            sub_field = None

        operator = self.get(key=Keys.operator)
        field = self.get(key=Keys.field)
        parser = ValueParser(
            field=field,
            value=value,
            operator=operator,
            sub_field=sub_field,
            apiobj=self.wizard.apiobj,
        )
        parsed = parser()
        self.parsed.update(parsed)
        return parsed
