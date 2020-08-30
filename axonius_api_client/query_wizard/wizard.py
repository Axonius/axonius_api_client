#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import copy
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from ..api.assets.asset_mixin import AssetMixin
from ..constants import ALL_NAME, LOG_LEVEL_WIZARD
from ..data_classes.fields import CUSTOM_FIELDS_MAP, Operator, OperatorTypeMaps
from ..data_classes.wizard import (
    ExprKeyDefaults,
    ExprKeys,
    ExprTypes,
    GuiExpr,
    Templates,
)
from ..exceptions import WizardError
from ..logs import get_obj_log
from ..tools import (
    check_empty,
    check_type,
    coerce_bool,
    coerce_int_float,
    coerce_str_to_csv,
    dt_parse_tmpl,
    get_raw_version,
    json_dump,
    parse_ip_address,
    parse_ip_network,
)
from .wizard_text import WizardText

SRC: str = "list of dictionaries"


class Wizard:

    DEFAULT_TYPE = ExprTypes.SIMPLE

    def __init__(
        self,
        apiobj: AssetMixin,
        log_exprs: bool = False,
        log_level: Union[str, int] = LOG_LEVEL_WIZARD,
    ):
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        self.apiobj: AssetMixin = apiobj
        self.aql: str = ""
        self.exprs: List[dict] = []
        self._error_stop: bool = True
        self._log_exprs: bool = log_exprs

    def parse(
        self, exprs: List[dict], error_stop: bool = True
    ) -> Tuple[str, List[dict]]:
        self.exprs: List[dict] = exprs
        self._error_stop: bool = error_stop

        check_type(value=exprs, name="exprs", exp=list, exp_items=dict)
        check_empty(value=exprs, name="exprs")

        self.LOG.debug(f"Parsing {len(exprs)} exprs")

        aqls = []
        gui_exprs = []

        expr_types = ExprTypes.get_values()
        for idx, expr in enumerate(exprs):
            expr[ExprKeys.IDX] = idx
            aql_expr, gui_expr = self._parse_expr(expr=expr, expr_types=expr_types)
            if aql_expr:
                aqls.append(aql_expr)

            if gui_expr:
                gui_exprs += gui_expr

        self.aql = aql = " ".join(aqls)
        self.LOG.info(f"Final AQL produced: {aql}")

        GuiExpr.set_idx(exprs=gui_exprs, first=False)
        if self._log_exprs:
            self.LOG.debug(f"Final GUI exprs produced: {json_dump(gui_exprs)}")

        return aql, gui_exprs

    def parse_text_str(self, content: str) -> Tuple[str, List[dict]]:
        self._wizard = WizardText(log_level=self.LOG.level, log_exprs=self._log_exprs)
        exprs = self._wizard.from_text(content=content)
        return self.parse(exprs=exprs)

    def parse_text_path(self, path: str) -> Tuple[str, List[dict]]:
        self._wizard = WizardText(log_level=self.LOG.level, log_exprs=self._log_exprs)
        exprs = self._wizard.from_path(path=path)
        return self.parse(exprs=exprs)

    def _parse_expr(self, expr: dict, expr_types: List[str]) -> Tuple[str, List[dict]]:
        orig_expr = copy.deepcopy(expr)
        try:
            check_type(value=expr, name="expression", exp=dict)

            key = ExprKeys.TYPE
            expr[key] = expr_type = expr.get(key, self.DEFAULT_TYPE).strip().lower()
            if expr_type not in expr_types:
                valid = "\n - " + "\n - ".join(expr_types)
                raise WizardError(f"Invalid type {expr_type!r}, valids:{valid}")

            return getattr(self, f"_handle_{expr_type}")(expr=expr)
        except Exception as exc:
            expr_lines = self._get_expr_lines(expr=orig_expr)
            msg = f"Error in expr:\n\n{expr_lines}\n\n{exc}"
            if self._error_stop:
                raise WizardError(msg)
            self.LOG.exception(msg)
        return "", []

    def _get_expr_lines(self, expr: dict, indent=0) -> str:
        itxt = " " * indent
        expr_lines = []

        for k, v in expr.items():
            if k.startswith("_"):
                continue

            if k == ExprKeys.SUBS:
                expr_lines.append(f"{itxt}- {k}:")
                for sub in v:
                    lines = ["", self._get_expr_lines(expr=sub, indent=indent + 2)]
                    expr_lines += lines
            elif isinstance(v, dict):
                expr_lines.append(f"{itxt}- {k}:")
                expr_lines += [f"{itxt}  - {a}: {b}" for a, b in v.items()]
            else:
                expr_lines.append(f"{itxt}- {k}: {v}")

        expr_lines += []
        return "\n".join(expr_lines)

    def _get_type(self, expr: dict, expr_types: List[str]) -> str:
        key = ExprKeys.TYPE
        value = expr.get(key, self.DEFAULT_TYPE).strip().lower()
        if value not in expr_types:
            valid = "\n - " + "\n - ".join(expr_types)
            raise WizardError(f"Invalid type {value!r}, valids:{valid}")

        expr[key] = value
        return value

    def _get_key(self, expr: dict, key: str) -> str:
        if key not in expr:
            raise WizardError(f"Key {key!r} must be defined")

        return expr[key]

    def _get_str(self, expr: dict, key: str) -> str:
        value = self._get_key(expr=expr, key=key)

        if not isinstance(value, str) or not value:
            vtype = type(value).__name__
            raise WizardError(f"Key {key!r} must be a non-empty string, not {vtype}")

        return value.strip().lower()

    def _get_operator(self, expr: dict) -> Operator:
        key = ExprKeys.OP

        if key not in expr:
            if ExprKeys.VALUE in expr:
                expr[key] = ExprKeyDefaults.OP_VALUE
            else:
                expr[key] = ExprKeyDefaults.OP_NO_VALUE

        field = self._get_field(expr=expr)
        value = self._get_str(expr=expr, key=key)
        op = OperatorTypeMaps.get_operator(field=field, operator=value)
        return op

    def _get_complex_sub_exprs(self, expr: dict) -> List[dict]:
        field = self._get_complex_field(expr=expr)
        fname = field["name"]
        key = ExprKeys.SUBS
        value = self._get_key(expr=expr, key=key)
        if not value:
            raise WizardError(
                f"No complex sub-exprs in {key!r}: {value!r} for field {fname!r}"
            )
        return value

    def _get_bracket_sub_exprs(self, expr: dict) -> List[dict]:
        key = ExprKeys.SUBS
        value = self._get_key(expr=expr, key=key)
        if not value:
            raise WizardError(f"No bracket sub-exprs in {key!r}: {value!r}")
        return value

    def _get_or_flag(self, expr: dict) -> str:
        key = ExprKeys.OR
        default = ExprKeyDefaults.OR
        expr[key] = value = coerce_bool(expr.get(key, default))
        return value

    def _get_comp_op(self, expr: dict) -> str:
        return Templates.OR if self._get_or_flag(expr=expr) else Templates.AND

    def _get_not_flag(self, expr: dict) -> str:
        key = ExprKeys.NOT
        default = ExprKeyDefaults.NOT
        expr[key] = value = coerce_bool(expr.get(key, default))
        return value

    def _get_aql_logic(self, expr: dict) -> str:
        value = []

        if expr[ExprKeys.IDX]:
            value.append(self._get_comp_op(expr=expr))

        if self._get_not_flag(expr=expr):
            value.append(Templates.NOT)

        if value:
            value.append("")

        return " ".join(value)

    def _get_field(self, expr: dict) -> dict:
        key = ExprKeys.FIELD

        if isinstance(expr.get(key), dict):
            return expr[key]

        field = self._get_str(expr=expr, key=key)
        field = self.apiobj.fields.get_field_name(
            value=field,
            fields_map=self._get_api_fields(),
            key=None,
            custom_fields_map=CUSTOM_FIELDS_MAP,
        )
        if field["name"] == ALL_NAME:
            raise WizardError(f"Can not use field {ALL_NAME!r} in queries")

        expr[key] = field
        return field

    def _get_complex_field(self, expr: dict) -> dict:
        field = self._get_field(expr=expr)

        adapter = field["adapter_name"]
        field_name = field["name"]

        if not field["is_complex"]:
            schemas = [
                x
                for x in self._get_api_fields()[adapter]
                if x["is_complex"] and x["name"] != ALL_NAME
            ]
            msg = [
                f"Invalid complex field {field_name!r} for {adapter}, valids:",
                *self.apiobj.fields._prettify_schemas(schemas=schemas),
            ]
            msg = "\n".join(msg)
            raise WizardError(msg)

        return field

    def _get_aql_logic_bracket(self, expr: dict, aql: str) -> str:
        bracket = expr.get(ExprKeys.BRACKET, {})
        pre = "(" if bracket.get(ExprKeys.BRACKET_LEFT) else ""
        post = ")" if bracket.get(ExprKeys.BRACKET_RIGHT) else ""
        aql = self._get_aql_logic(expr=expr) + f"{pre}{aql}{post}"
        return aql

    def _handle_simple(self, expr: dict) -> Tuple[str, List[dict]]:
        op = self._get_operator(expr=expr)
        op_logic = self._get_comp_op(expr=expr) if expr[ExprKeys.IDX] else ""
        not_flag = self._get_not_flag(expr=expr)
        field = self._get_field(expr=expr)

        aql = self._value_parser(expr=expr)
        expr[ExprKeys.AQL] = aql = self._get_aql_logic_bracket(expr=expr, aql=aql)
        self.LOG.info(f"Simple AQL produced: {aql}")

        bracket = expr.get(ExprKeys.BRACKET, {})
        expr[ExprKeys.EXPR_GUI] = expr_gui = GuiExpr.get(
            aql=aql,
            field=field["name"],
            field_type=field["expr_field_type"],
            op_comp=op.name_map.op,
            value=expr[ExprKeys.EVALUE],
            op_logic=op_logic,
            not_flag=not_flag,
            **bracket,
        )
        if self._log_exprs:
            self.LOG.debug(f"Simple GUI expr produced:\n{json_dump(expr_gui)}")

        return aql, [expr_gui]

    def _handle_complex(self, expr: dict) -> Tuple[str, List[dict]]:
        field = self._get_complex_field(expr=expr)
        op_logic = self._get_comp_op(expr=expr) if expr[ExprKeys.IDX] else ""
        not_flag = self._get_not_flag(expr=expr)

        sub_exprs = self._get_complex_sub_exprs(expr=expr)
        self.LOG.debug(f"Parsing {len(sub_exprs)} complex sub-exprs")

        sub_aqls = []
        sub_gui_exprs = []
        for sub_expr in sub_exprs:
            sub_aql_expr, sub_gui_expr = self._complex_sub(expr=expr, sub_expr=sub_expr)
            sub_aqls.append(sub_aql_expr)
            sub_gui_exprs.append(sub_gui_exprs)

        tmpl = Templates.COMPLEX.format
        aql = tmpl(field=field["name"], sub_aqls=f" {Templates.AND} ".join(sub_aqls))
        expr[ExprKeys.AQL] = aql = self._get_aql_logic_bracket(expr=expr, aql=aql)
        self.LOG.info(f"Complex AQL produced: {aql}")

        bracket = expr.get(ExprKeys.BRACKET, {})
        expr[ExprKeys.EXPR_GUI] = expr_gui = GuiExpr.get_complex(
            aql=aql,
            field=field["name"],
            field_type=field["expr_field_type"],
            children=sub_gui_exprs,
            op_logic=op_logic,
            not_flag=not_flag,
            **bracket,
        )
        if self._log_exprs:
            self.LOG.debug(f"Complex GUI expr produced:\n{json_dump(expr_gui)}")

        return aql, [expr_gui]

    def _handle_bracket(self, expr: dict) -> Tuple[str, List[dict]]:
        sub_exprs = self._get_bracket_sub_exprs(expr=expr)
        self.LOG.debug(f"Parsing {len(sub_exprs)} bracket sub-exprs")

        aqls = []
        gui_exprs = []
        expr_types = [ExprTypes.COMPLEX, ExprTypes.SIMPLE]

        for idx, sub_expr in enumerate(sub_exprs):
            bracket = {}
            bracket[ExprKeys.BRACKET_LEFT] = idx == 0
            bracket[ExprKeys.BRACKET_RIGHT] = idx == len(sub_exprs) - 1
            bracket[ExprKeys.BRACKET_WEIGHT] = idx - 1
            sub_expr[ExprKeys.BRACKET] = bracket
            sub_expr[ExprKeys.IDX] = idx + expr[ExprKeys.IDX]
            aql_expr, gui_expr = self._parse_expr(expr=sub_expr, expr_types=expr_types)

            if aql_expr:
                aqls.append(aql_expr)

            if gui_expr:
                gui_exprs += gui_expr

        expr[ExprKeys.AQL] = aql = " ".join(aqls)
        self.LOG.info(f"Bracket AQL produced: {aql}")
        expr[ExprKeys.EXPR_GUI] = gui_exprs
        return aql, gui_exprs

    def _complex_sub(self, expr: dict, sub_expr: dict) -> Tuple[str, dict]:
        check_type(value=sub_expr, exp=dict, name="complex sub-field")

        field = self._get_complex_field(expr=expr)
        field_name = field["name"]
        field_subs = {x["name"]: x for x in field["sub_fields"]}

        sub_name = self._get_str(expr=sub_expr, key=ExprKeys.SUB)
        if sub_name not in field_subs:
            valid = "\n - " + "\n - ".join(list(field_subs))
            raise WizardError(
                f"{sub_name!r} is not a sub field of {field_name!r}, valids:{valid}"
            )

        sub_expr[ExprKeys.FIELD] = field_subs[sub_name]
        sub_field_name = field_subs[sub_name]["name"]
        op = self._get_operator(expr=sub_expr)
        aql = self._value_parser(expr=sub_expr)
        sub_expr[ExprKeys.AQL] = aql
        self.LOG.info(f"Complex sub-field AQL produced: {aql}")

        expr_gui = GuiExpr.get_child(
            aql=aql,
            field=sub_field_name,
            op_comp=op.name_map.op,
            value=sub_expr[ExprKeys.EVALUE],
        )
        sub_expr[ExprKeys.EXPR_GUI] = expr_gui

        if self._log_exprs:
            self.LOG.debug(
                f"Complex sub-field GUI expr produced:\n{json_dump(expr_gui)}"
            )

        return aql, expr_gui

    def _value_parser(self, expr: dict) -> str:
        field = self._get_field(expr=expr)
        field_name = field["name"]

        op = self._get_operator(expr=expr)
        parser = f"_value_{op.parser.name}"
        method = getattr(self, parser, None)

        if not method:
            raise WizardError(f"No parser implemented for {parser!r}")

        pvalue = method(expr=expr)

        tmpl = op.template.format
        aql = tmpl(field=field_name, parsed_value=pvalue)
        return aql

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
            for item in enum:
                item_check = item.lower() if isinstance(item, str) else item
                value_check = value.lower() if isinstance(value, str) else value
                if item_check == value_check:
                    return item

            valid = "\n - " + "\n - ".join([str(x) for x in enum])
            raise WizardError(f"invalid choice {value!r}, valid choices:{valid}")

        if isinstance(enum, dict):
            for item, item_value in enum.items():
                item_check = item.lower() if isinstance(item, str) else item
                value_check = value.lower() if isinstance(value, str) else value
                if item_check == value_check:
                    return item_value

            valid = "\n - " + "\n - ".join([str(x) for x in enum])
            raise WizardError(f"invalid choice {value!r}, valid choices:{valid}")

        etype = type(enum).__name__
        raise WizardError(f"Unhandled enum type {etype}: {enum}")

    def _check_str_value(self, value) -> str:
        check_type(value=value, exp=str)
        check_empty(value=value, name=f"{ExprKeys.VALUE} key")
        return value

    def _value_to_str(self, expr: dict) -> str:
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        field = self._get_field(expr=expr)
        pvalue = self._check_enum(value=value, field=field)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue
        return pvalue

    def _value_to_int(self, expr: dict) -> int:
        value = expr.get(ExprKeys.VALUE, "")
        pvalue = coerce_int_float(value=value)

        field = self._get_field(expr=expr)
        pvalue = self._check_enum(value=pvalue, field=field)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue
        return pvalue

    def _value_none(self, expr: dict) -> None:
        pvalue = None

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue
        return pvalue

    def _value_to_raw_version(self, expr: dict) -> str:
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        pvalue = get_raw_version(value=value)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = value
        return pvalue

    def _value_to_dt(self, expr: dict) -> str:
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        pvalue = dt_parse_tmpl(obj=value)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue
        return pvalue

    def _value_to_ip(self, expr: dict):
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        pvalue = str(parse_ip_address(value=value))

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue
        return pvalue

    def _value_to_subnet(self, expr: dict) -> str:
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        pvalue = str(parse_ip_network(value=value))

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue
        return pvalue

    def _value_ip_to_subnet_start_end(self, expr: dict) -> str:
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        ip_network = parse_ip_network(value=value)
        start = int(ip_network.network_address)
        end = int(ip_network.broadcast_address)

        evalue = str(ip_network)
        pvalue = [start, end]

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = evalue
        return pvalue

    def _value_to_escaped_regex(self, expr: dict) -> str:
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        pvalue = re.escape(value)

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = value
        return pvalue

    def _value_to_str_tags(self, expr: dict) -> str:
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        field = self._get_field(expr=expr)

        pvalue = self._check_enum(value=value, field=field, extra=self._get_api_tags())

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue
        return pvalue

    def _value_to_str_adapters(self, expr: dict) -> str:
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        field = self._get_field(expr=expr)

        pvalue = self._check_enum(
            value=value, field=field, extra=self._get_api_adapter_names()
        )

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue
        return pvalue

    def _value_to_str_cnx_label(self, expr: dict) -> str:
        value = expr.get(ExprKeys.VALUE, "")
        self._check_str_value(value=value)

        check_type(value=value, exp=str)

        field = self._get_field(expr=expr)

        pvalue = self._check_enum(
            value=value, field=field, extra=self._get_api_adapter_cnx_labels()
        )

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = pvalue
        return pvalue

    def _value_to_csv(
        self,
        expr: dict,
        value: Union[int, str],
        item_method: Any,
        join_tmpl: str = '"{}"',
        post_method: Optional[Any] = None,
        enum_extra: Optional[List[Union[int, str]]] = None,
    ) -> str:
        items = coerce_str_to_csv(value=value)
        field = self._get_field(expr=expr)

        new_items = []
        for idx, item in enumerate(items):
            item_num = idx + 1
            try:
                item = item_method(item)

                if post_method:
                    item = post_method(item)

                item = self._check_enum(field=field, value=item, extra=enum_extra)
                new_items.append(item)
            except Exception as exc:
                raise WizardError(f"Error in item #{item_num} of {len(items)}: {exc}")

        pvalue = ", ".join([join_tmpl.format(x) for x in new_items])
        evalue = ",".join([str(x) for x in new_items])

        expr[ExprKeys.PVALUE] = pvalue
        expr[ExprKeys.EVALUE] = evalue
        return pvalue

    def _value_to_csv_str(self, expr: dict) -> str:
        pvalue = self._value_to_csv(expr=expr, item_method=self._check_str_value)
        return pvalue

    def _value_to_csv_int(self, expr: dict) -> str:
        pvalue = self._value_to_csv(
            expr=expr, item_method=coerce_int_float, join_tmpl="{}"
        )
        return pvalue

    def _value_to_csv_subnet(self, expr: dict) -> str:
        pvalue = self._value_to_csv(
            expr=expr, item_method=parse_ip_network, post_method=str
        )
        return pvalue

    def _value_to_csv_ip(self, expr: dict) -> str:
        pvalue = self._value_to_csv(
            expr=expr, item_method=parse_ip_address, post_method=str
        )
        return pvalue

    def _value_to_csv_tags(self, expr: dict) -> str:
        pvalue = self._value_to_csv(
            expr=expr, item_method=self._check_str_value, enum_extra=self._get_api_tags()
        )
        return pvalue

    def _value_to_csv_adapters(self, expr: dict) -> str:
        pvalue = self._value_to_csv(
            expr=expr,
            item_method=self._check_str_value,
            enum_extra=self._get_api_adapter_names(),
        )
        return pvalue

    def _value_to_csv_cnx_label(self, expr: dict) -> str:
        pvalue = self._value_to_csv(
            expr=expr,
            item_method=self._check_str_value,
            enum_extra=self._get_api_adapter_cnx_labels(),
        )
        return pvalue

    def _get_api_fields(self) -> Dict[str, List[dict]]:
        if not hasattr(self, "_api_fields"):
            self._api_fields = self.apiobj.fields.get()
        return self._api_fields

    def _get_api_tags(self) -> List[str]:
        if not hasattr(self, "_api_tags"):
            self._api_tags = self.apiobj.labels.get()
        return self._api_tags

    def _get_api_adapters(self) -> List[dict]:
        if not hasattr(self, "_api_adapters"):
            self._api_adapters = self.apiobj.adapters.get()
        return self._api_adapters

    def _get_api_adapter_names(self) -> Dict[str, str]:
        return {x["name"]: x["name_raw"] for x in self._get_api_adapters() if x["cnx"]}

    def _get_api_adapter_cnx_labels(self) -> List[str]:
        value = []
        for adapter in self._get_api_adapters():
            for cnx in adapter["cnx"]:
                config = cnx.get("config", {})
                label = config.get("connection_label", "")
                if label and label not in value:
                    value.append(label)
        return value
