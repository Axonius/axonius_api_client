#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import logging
import re
from typing import Any, Dict, List, Optional, Union

from ..constants import AGG_ADAPTER_NAME, LOG_LEVEL_WIZARD
from ..data_classes.fields import Operator, OperatorTypeMap, OperatorTypeMaps
from ..exceptions import WizardError
from ..logs import get_obj_log
from ..tools import (
    check_type,
    coerce_int,
    coerce_str_to_csv,
    dt_parse_tmpl,
    get_raw_version,
    parse_ip_address,
    parse_ip_network,
)


class ValueParser:
    def __init__(self, apiobj, field: dict, operator: str, value: Any, **kwargs):
        log_level: str = kwargs.get("log_level", LOG_LEVEL_WIZARD)
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        self.apiobj = apiobj
        self.field = field
        self._operator = operator
        self.value = value

    def __str__(self) -> str:
        items = [
            f"field: {self.field['column_name']!r}",
            f"type: {self.field['type_norm']!r}",
            f"operator: {self._operator!r}",
            f"value: {self.value!r}",
        ]
        return ", ".join([x for x in items if x])

    def __call__(self) -> dict:
        self.LOG.debug(f"Parsing {self}")

        parser_name = self.operator.parser.value
        parser = getattr(self, parser_name, None)
        if not parser:
            raise WizardError(
                f"No parser implemented for {parser_name!r} while in {self}!"
            )
        return parser()

    @property
    def api_tags(self):
        if not hasattr(self.apiobj, "_api_tags"):
            self.apiobj._api_tags = self.apiobj.labels.get()
        return self.apiobj._api_tags

    @property
    def api_adapters(self):
        if not hasattr(self.apiobj, "_api_adapters"):
            self.apiobj._api_adapters = self.apiobj.adapters.get()
        return self.apiobj._api_adapters

    @property
    def api_adapter_names(self):
        return {x["name"]: x["name_raw"] for x in self.api_adapters if x["cnx"]}

    @property
    def api_adapter_cnx_labels(self):
        value = []
        for adapter in self.api_adapters:
            for cnx in adapter["cnx"]:
                config = cnx.get("config", {})
                label = config.get("connection_label", "")
                if label and label not in value:
                    value.append(label)
        return value

    @property
    def expr_field_type(self):
        if self.field["adapter_name"] == AGG_ADAPTER_NAME:
            return "axonius"
        return self.field["adapter_name_raw"]

    @property
    def enum(self) -> list:
        return self.field.get("enum") or []

    @property
    def items_enum(self) -> list:
        items = self.field.get("items") or {}
        return items.get("enum") or []

    @property
    def operator_type_map(self) -> OperatorTypeMap:
        return getattr(OperatorTypeMaps, self.field["type_norm"])

    @property
    def valid_operators(self) -> Dict[str, OperatorTypeMap]:
        return {x.name.name: x for x in self.operator_type_map.operators}

    @property
    def operator(self) -> Operator:
        if self._operator not in self.valid_operators:
            valid = "\n  " + "\n  ".join(list(self.valid_operators))
            raise WizardError(f"Invalid operator for {self}, valid operators: {valid}")
        return self.valid_operators[self._operator]

    @property
    def template_field(self):
        if self._sub_field:
            return self._sub_field["name"]
        return self._field["name_qual"]

    def check_enum(
        self, value: Union[int, str], extra: Optional[List[str]] = None
    ) -> Union[int, str]:
        enum = self.items_enum or self.enum or extra or []

        if not enum:
            return value

        if isinstance(enum, (list, tuple)):
            if value in enum:
                return value
            valid = "\n - " + "\n - ".join([str(x) for x in enum])
            raise WizardError(f"invalid choice {value!r}, valid choices: {valid}")

        if isinstance(enum, dict):
            if value in enum:
                return enum[value]
            valid = "\n - " + "\n - ".join([str(x) for x in enum])
            raise WizardError(f"invalid choice {value!r}, valid choices: {valid}")

        etype = type(enum).__name__
        raise WizardError(f"Unhandled enum type {etype}: {enum}")

    def templater(self, parsed_value: Any, expr_value: Optional[Any] = None, **kwargs):
        if expr_value is None:
            expr_value = parsed_value

        kwargs["field"] = self.field["name"]
        aql = self.operator.template.format(parsed_value=parsed_value, **kwargs)
        self.LOG.info(f"AQL produced: {aql}")

        expr = {
            "value": expr_value,
            "operator": self.operator.name.value,
            "field": self.field["name"],
            "field_type": self.field["expr_field_type"],
        }
        return {"aql": aql, "sq_expr": expr}

    def to_str(self):
        parsed_value = self.check_enum(value=str(self.value))
        return self.templater(parsed_value=parsed_value)

    def to_int(self):
        parsed_value = self.check_enum(value=coerce_int(obj=self.value))
        return self.templater(parsed_value=parsed_value)

    def none(self):
        return self.templater(parsed_value=None)

    def to_raw_version(self):
        check_type(value=self.value, exp=str)
        parsed_value = get_raw_version(value=self.value)
        return self.templater(parsed_value=parsed_value, expr_value=self.value)

    def to_csv(self, item_method, join_tmpl='"{}"', post_method=None, enum_extra=None):
        items = coerce_str_to_csv(value=self.value)
        new_items = []
        for idx, item in enumerate(items):
            try:
                item = item_method(item)
                if post_method:
                    item = post_method(item)
                item = self.check_enum(value=item, extra=enum_extra)
                new_items.append(item)
            except Exception as exc:
                raise WizardError(f"Error in item #{idx + 1} of {len(items)}: {exc}")

        parsed_value = ", ".join([join_tmpl.format(x) for x in new_items])
        expr_value = ",".join([str(x) for x in new_items])
        return self.templater(parsed_value=parsed_value, expr_value=expr_value)

    def to_csv_str(self):
        return self.to_csv(item_method=str)

    def to_csv_int(self):
        return self.to_csv(item_method=coerce_int, join_tmpl="{}")

    def to_csv_subnet(self):
        return self.to_csv(item_method=parse_ip_network, post_method=str)

    def to_csv_ip(self):
        return self.to_csv(item_method=parse_ip_address, post_method=str)

    def to_csv_tags(self):
        return self.to_csv(item_method=str, enum_extra=self.api_tags)

    def to_csv_adapters(self):
        return self.to_csv(item_method=str, enum_extra=self.api_adapter_names)

    def to_csv_cnx_label(self):
        return self.to_csv(item_method=str, enum_extra=self.api_adapter_cnx_labels)

    def to_dt(self):
        parsed_value = dt_parse_tmpl(obj=self.value)
        return self.templater(parsed_value=parsed_value)

    def to_ip(self):
        check_type(value=self.value, exp=str)
        parsed_value = str(parse_ip_address(value=self.value))
        return self.templater(parsed_value=parsed_value)

    def to_subnet(self):
        check_type(value=self.value, exp=str)
        parsed_value = str(parse_ip_network(value=self.value))
        return self.templater(parsed_value=parsed_value)

    def ip_to_subnet_start_end(self):
        check_type(value=self.value, exp=str)
        ip_network = parse_ip_network(value=self.value)
        expr_value = str(ip_network)
        start = int(ip_network.network_address)
        end = int(ip_network.broadcast_address)
        parsed_value = [start, end]
        return self.templater(parsed_value=parsed_value, expr_value=expr_value)

    def to_escaped_regex(self):
        check_type(value=self.value, exp=str)
        parsed_value = re.escape(self.value)
        return self.templater(parsed_value=parsed_value, expr_value=self.value)

    def to_str_tags(self):
        check_type(value=self.value, exp=str)
        parsed_value = self.check_enum(value=self.value, extra=self.api_tags)
        return self.templater(parsed_value=parsed_value)

    def to_str_adapters(self):
        check_type(value=self.value, exp=str)
        parsed_value = self.check_enum(value=self.value, extra=self.api_adapter_names)
        return self.templater(parsed_value=parsed_value)

    def to_str_cnx_label(self):
        check_type(value=self.value, exp=str)
        parsed_value = self.check_enum(
            value=self.value, extra=self.api_adapter_cnx_labels
        )
        return self.templater(parsed_value=parsed_value)
