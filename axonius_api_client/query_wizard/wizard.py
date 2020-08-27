#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import copy
import logging
import re
from typing import Any, Dict, List, Optional, Union

from ..api.assets.asset_mixin import AssetMixin
from ..constants import LOG_LEVEL_WIZARD
from ..data_classes.fields import CUSTOM_FIELDS_MAP, Operator, OperatorTypeMaps
from ..data_classes.wizard import ExprKeyDefaults, ExprKeys, ExprTypes, LogTypes
from ..exceptions import WizardError
from ..logs import get_obj_log
from ..tools import (
    check_empty,
    check_type,
    coerce_int,
    coerce_str_to_csv,
    dt_parse_tmpl,
    get_raw_version,
    parse_ip_address,
    parse_ip_network,
)

SRC: str = "list of dictionaries"


class Wizard:

    DEFAULT_TYPE = ExprTypes.SIMPLE

    def __init__(self, apiobj: AssetMixin, **kwargs):
        log_level: str = kwargs.get("log_level", LOG_LEVEL_WIZARD)
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        self.apiobj: AssetMixin = apiobj

    def parse(self, exprs: List[dict], source: str = SRC) -> dict:
        err = "Expressions must be a list with at least one dictionary"

        if not isinstance(exprs, list):
            vtype = type(exprs).__name__
            raise WizardError(f"{err}, not type {vtype}")

        if not exprs:
            raise WizardError(f"{err}, not an empty list")

        for idx, expr in enumerate(exprs):
            self._parse_expr(expr=expr, idx=idx, source=source)

        return exprs

    def _parse_expr(self, expr: dict, idx: int, source: str):
        orig_expr = copy.deepcopy(expr)

        try:
            if not isinstance(expr, dict):
                vtype = type(expr).__name__
                raise WizardError(f"Expression must be a dictionary, not type {vtype}")

            expr_type = self._get_type(expr=expr)
            getattr(self, f"_handle_{expr_type}")(expr=expr)
        except Exception as exc:
            expr_lines = self._get_expr_lines(expr=orig_expr)
            raise WizardError(
                f"Error in expression #{idx + 1} from {source}:{expr_lines}{exc}"
            )

    @staticmethod
    def _get_expr_lines(expr: dict) -> str:
        expr_lines = ["", ""]

        for k, v in expr.items():
            if k.startswith("_"):
                continue

            if isinstance(v, dict):
                expr_lines.append(f" - {k}:")
                expr_lines += [f"   -  {a}: {b}" for a, b in v.items()]
            else:
                expr_lines.append(f" - {k}: {v}")

        expr_lines += ["", ""]
        return "\n".join(expr_lines)

    def _get_type(self, expr: dict) -> str:
        key = ExprKeys.TYPE

        if not isinstance(expr, dict):
            vtype = type(expr).__name__
            raise WizardError(f"Expression must be a dictionary, not type {vtype}")

        expr_type = expr.get(key, self.DEFAULT_TYPE).strip().lower()
        expr_types = ExprTypes.get_values()

        if expr_type not in expr_types:
            valid = ExprTypes.JOIN(expr_types)
            raise WizardError(f"Invalid type {expr_type!r}, valids:{valid}")

        expr[key] = expr_type
        return expr_type

    def _get_str(self, expr: dict, key: str) -> str:
        value = expr[key]

        if not isinstance(value, str) or not value:
            vtype = type(expr).__name__
            raise WizardError(f"Key {key!r} must be a non-empty string, not {vtype}")

        return value.strip().lower()

    def _get_operator(self, expr: dict) -> Operator:
        key = ExprKeys.OP

        if key not in expr:
            if ExprKeys.VALUE in expr:
                expr[key] = ExprKeyDefaults.OP_VALUE
            else:
                expr[key] = ExprKeyDefaults.OP_NO_VALUE

        field = expr[ExprKeys.FIELD]
        operator = self._get_str(expr=expr, key=key)
        op = OperatorTypeMaps.get_operator(field=field, operator=operator)

        expr[key] = op
        return op

    def _get_subs(self, expr: dict):
        pass

    def _get_logical(self, expr: dict) -> str:
        key = ExprKeys.LOG

        if key not in expr:
            expr[key] = ExprKeyDefaults.LOG

        log_type = self._get_str(expr=expr, key=key)
        log_types = LogTypes.get_values()

        if log_type not in log_types:
            valid = LogTypes.get_values(join="\n - ")
            raise WizardError(f"Invalid logical operator {log_type!r}, valids:{valid}")

        expr[key] = log_type
        return log_type

    def _get_field(self, expr: dict) -> dict:
        key = ExprKeys.FIELD

        field = self._get_str(expr=expr, key=key)
        field = self.apiobj.fields.get_field_name(
            value=field,
            fields_map=self.api_fields,
            key=None,
            custom_fields_map=CUSTOM_FIELDS_MAP,
        )

        expr[key] = field
        return field

    def _get_complex_field(self, expr: dict) -> dict:
        field = self._get_field(expr=expr)

        adapter = field["adapter_name"]
        field_name = field["name"]

        if not field["is_complex"]:
            schemas = [
                x
                for x in self.api_fields[adapter]
                if x["is_complex"] and x["name"] != "all"
            ]
            msg = [
                f"Invalid complex field {field_name!r}",
                f"Valid complex fields for {adapter}:",
                *self.apiobj.fields._prettify_schemas(schemas=schemas),
            ]
            msg = "\n".join(msg)
            raise WizardError(msg)

        return field

    def _get_sub_field(self, expr, sub_expr):
        pass

    def _handle_simple(self, expr: dict):
        # field, operator, logical, value
        self._get_field(expr=expr)
        self._get_logical(expr=expr)
        self._get_operator(expr=expr)
        self._value_parser(expr=expr)

    def _handle_complex(self, expr: dict):
        # field, subs, logical
        # subs: field, operator, value
        pass

    def _handle_bracket(self, expr: dict):
        # subs
        # subs: simple or complex based on type
        pass

    def _value_parser(self, expr: dict) -> Any:
        op = expr[ExprKeys.OP]
        parser = f"_value_{op.parser.value}"

        if not hasattr(self, parser):
            raise WizardError(f"No parser implemented for {parser!r}")

        parser(expr=expr)

    def _check_enum(
        self, value: Union[int, str], field: dict, extra: Optional[List[str]] = None
    ) -> Union[int, str]:
        enum = field.get("enum") or []
        items = field.get("items") or {}
        items_enum = items.get("enum") or []

        enum = items_enum or enum or extra or []

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

    def _get_aql(self, expr: dict):
        field = expr[ExprKeys.FIELD]
        pvalue = expr[ExprKeys.PVALUE]
        op = expr[ExprKeys.OP]

        aql = op.template.format(field=field["name"], parsed_value=pvalue)
        expr[ExprKeys.AQL] = aql
        self.LOG.info(f"AQL produced: {aql}")

    def _check_str_value(value):
        check_type(value=value, exp=str)
        check_empty(value=value, name=f"{ExprKeys.VALUE} key")
        return value

    def _value_to_str(self, expr: dict):
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        field = expr[ExprKeys.FIELD]
        pvalue = self._check_enum(value=value, field=field)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue

    def _value_to_int(self, expr: dict, field: dict) -> dict:
        value = expr.get(ExprKeys.VALUE, "")

        value = coerce_int(obj=value)
        field = expr[ExprKeys.FIELD]
        pvalue = self._check_enum(value=value, field=field)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue

    def _value_none(self, expr: dict, field: dict) -> dict:
        value = None

        expr[ExprKeys.PVALUE] = value
        expr[ExprKeys.EVALUE] = value

    def _value_to_raw_version(self, expr: dict):
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        pvalue = get_raw_version(value=value)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = value

    def _value_to_dt(self, expr: dict):
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        pvalue = dt_parse_tmpl(obj=value)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue

    def _value_to_ip(self, expr: dict):
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        pvalue = str(parse_ip_address(value=value))

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue

    def _value_to_subnet(self, expr: dict):
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        pvalue = str(parse_ip_network(value=value))

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue

    def _value_ip_to_subnet_start_end(self, expr: dict):
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        ip_network = parse_ip_network(value=value)
        start = int(ip_network.network_address)
        end = int(ip_network.broadcast_address)

        evalue = str(ip_network)
        pvalue = [start, end]

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = evalue

    def _value_to_escaped_regex(self, expr: dict):
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        pvalue = re.escape(value)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = value

    def _value_to_str_tags(self, expr: dict):
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        field = expr[ExprKeys.FIELD]
        pvalue = self._check_enum(value=value, field=field, extra=self.api_tags)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue

    def _value_to_str_adapters(self, expr: dict):
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        field = expr[ExprKeys.FIELD]
        pvalue = self._check_enum(value=value, field=field, extra=self.api_adapter_names)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue

    def _value_to_str_cnx_label(self, expr: dict):
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        check_type(value=value, exp=str)

        field = expr[ExprKeys.FIELD]
        pvalue = self._check_enum(
            value=value, field=field, extra=self.api_adapter_cnx_labels
        )

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue

    def _value_to_csv(
        self,
        expr: dict,
        value: Any,
        item_method: Any,
        join_tmpl: str = '"{}"',
        post_method: Optional[Any] = None,
        enum_extra: Optional[List[Union[int, str]]] = None,
    ):
        items = coerce_str_to_csv(value=value)

        value = expr[ExprKeys.FIELD]
        field = expr[ExprKeys.FIELD]

        new_items = []
        for idx, item in enumerate(items):
            try:
                item = item_method(item)

                if post_method:
                    item = post_method(item)

                item = self._check_enum(field=field, value=item, extra=enum_extra)
                new_items.append(item)
            except Exception as exc:
                raise WizardError(f"Error in item #{idx + 1} of {len(items)}: {exc}")

        pvalue = ", ".join([join_tmpl.format(x) for x in new_items])
        evalue = ",".join([str(x) for x in new_items])

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = evalue

    def _value_to_csv_str(self, expr: dict):
        self._value_to_csv(expr=expr, item_method=self._check_str_value)

    def _value_to_csv_int(self, expr: dict):
        self._value_to_csv(expr=expr, item_method=coerce_int, join_tmpl="{}")

    def _value_to_csv_subnet(self, expr: dict):
        self._value_to_csv(expr=expr, item_method=parse_ip_network, post_method=str)

    def _value_to_csv_ip(self, expr: dict):
        self._value_to_csv(expr=expr, item_method=parse_ip_address, post_method=str)

    def _value_to_csv_tags(self, expr: dict):
        self._value_to_csv(
            expr=expr, item_method=self._check_str_value, enum_extra=self.api_tags
        )

    def _value_to_csv_adapters(self, expr: dict):
        self._value_to_csv(
            expr=expr,
            item_method=self._check_str_value,
            enum_extra=self.api_adapter_names,
        )

    def _value_to_csv_cnx_label(self, expr: dict):
        self._value_to_csv(
            expr=expr,
            item_method=self._check_str_value,
            enum_extra=self.api_adapter_cnx_labels,
        )

    @property
    def api_fields(self) -> Dict[str, List[dict]]:
        if not hasattr(self, "_fields"):
            self._fields = self.apiobj.fields.get()
        return self._fields

    @property
    def api_tags(self) -> List[str]:
        if not hasattr(self.apiobj, "_api_tags"):
            self.apiobj._api_tags = self.apiobj.labels.get()
        return self.apiobj._api_tags

    @property
    def api_adapters(self) -> List[dict]:
        if not hasattr(self.apiobj, "_api_adapters"):
            self.apiobj._api_adapters = self.apiobj.adapters.get()
        return self.apiobj._api_adapters

    @property
    def api_adapter_names(self) -> Dict[str, str]:
        return {x["name"]: x["name_raw"] for x in self.api_adapters if x["cnx"]}

    @property
    def api_adapter_cnx_labels(self) -> List[str]:
        value = []
        for adapter in self.api_adapters:
            for cnx in adapter["cnx"]:
                config = cnx.get("config", {})
                label = config.get("connection_label", "")
                if label and label not in value:
                    value.append(label)
        return value
