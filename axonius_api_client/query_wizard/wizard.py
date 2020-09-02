#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities for this package."""
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from ..api.assets.asset_mixin import AssetMixin
from ..constants import ALL_NAME, LOG_LEVEL_WIZARD
from ..data_classes.fields import CUSTOM_FIELDS_MAP, Operator, OperatorTypeMaps
from ..data_classes.wizard import (ExprGuiKeys, ExprKeyDefaults, ExprKeys,
                                   ExprTypes, GuiExpr, Templates)
from ..exceptions import ToolsError, WizardError
from ..logs import get_obj_log
from ..tools import (check_empty, check_type, coerce_int_float,
                     coerce_str_to_csv, dt_parse_tmpl, get_raw_version,
                     json_dump, parse_ip_address, parse_ip_network)
from .tools import get_expr_lines, get_key_bool, get_key_lod, get_key_str
from .wizard_text import WizardText


class Wizard:
    def __init__(
        self,
        apiobj: AssetMixin,
        error_stop: bool = True,
        log_exprs: bool = False,
        log_aql: bool = False,
        log_parse: bool = False,
        log_level: Union[str, int] = LOG_LEVEL_WIZARD,
    ):
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        self.apiobj: AssetMixin = apiobj
        self._error_stop: bool = error_stop
        self._log_exprs: bool = log_exprs
        self._expr_log = self.LOG.debug if log_exprs else lambda x: x
        self._aql_log = self.LOG.info if log_aql else lambda x: x
        self._parse_log = self.LOG.debug if log_parse else lambda x: x

    def parse(self, exprs: List[dict]) -> Tuple[str, List[dict]]:
        check_type(value=exprs, exp=(list, tuple), name="expressions", exp_items=dict)
        check_empty(value=exprs, name="expressions")

        self._parse_log(f"Parsing {len(exprs)} exprs")

        aqls = []
        gui_exprs = []
        valid = ExprTypes.get_all_types()
        for idx, expr in enumerate(exprs):
            expr_type = self._get_type(expr=expr, valid=valid)
            expr_method = getattr(self, f"_handle_{expr_type}")

            try:
                expr_aql, exprs_gui = expr_method(expr=expr, idx=idx)
            except WizardError:
                raise
            except Exception as exc:
                lines = get_expr_lines(expr=expr)
                msg = f"Error in expression #{idx}: {exc}\n\n{lines}"
                if self._error_stop:
                    raise WizardError(msg)
                self.LOG.exception(msg)
                continue

            aqls.append(expr_aql)
            gui_exprs += exprs_gui

        aql = " ".join([x for x in aqls if x])
        gui_exprs = [x for x in gui_exprs if x]
        for idx, gui_expr in enumerate(gui_exprs):
            gui_expr[ExprGuiKeys.IDX] = idx

        self._aql_log(f"Final AQL produced: {aql}")
        self._expr_log(f"Final GUI exprs produced: {json_dump(gui_exprs)}")

        return aql, gui_exprs

    def parse_text_str(self, content: str) -> Tuple[str, List[dict]]:
        self._wizard = WizardText(log_level=self.LOG.level, log_exprs=self._log_exprs)
        exprs = self._wizard.from_text(content=content)
        return self.parse(exprs=exprs)

    def parse_text_path(self, path: str) -> Tuple[str, List[dict]]:
        self._wizard = WizardText(log_level=self.LOG.level, log_exprs=self._log_exprs)
        exprs = self._wizard.from_path(path=path)
        return self.parse(exprs=exprs)

    def _handle_simple(
        self, expr: dict, idx: int, bracket: Optional[dict] = None
    ) -> Tuple[str, List[dict]]:
        or_flag = self._get_or_flag(expr=expr)
        not_flag = self._get_not_flag(expr=expr)
        field = self._get_field(expr=expr)
        operator = self._get_operator(expr=expr, field=field)

        aql, parsed_value, expr_value = self._value_parser(
            expr=expr, field=field, operator=operator
        )
        aql = GuiExpr.aql_add_logic(
            or_flag=or_flag, not_flag=not_flag, aql=aql, idx=idx, bracket=bracket,
        )

        gui_expr = GuiExpr.get(
            aql=aql,
            field=field["name"],
            field_type=field["expr_field_type"],
            op_comp=operator.name_map.op,
            value=expr_value,
            not_flag=not_flag,
            or_flag=or_flag,
            idx=idx,
            **bracket or {},
        )

        self._aql_log(f"Simple AQL produced: {aql}")
        self._expr_log(f"Simple GUI expr produced:\n{json_dump(gui_expr)}")
        return aql, [gui_expr]

    def _handle_complex(
        self, expr: dict, idx: int, bracket: Optional[dict] = None
    ) -> Tuple[str, List[dict]]:
        field = self._get_field(expr=expr, is_complex=True)
        field_subs = {x["name"]: x for x in field["sub_fields"]}
        not_flag = self._get_not_flag(expr=expr)
        or_flag = self._get_or_flag(expr=expr)
        sub_exprs = get_key_lod(key=ExprKeys.SUBS, expr=expr)

        self._parse_log(f"Parsing {len(sub_exprs)} complex sub-exprs")

        aqls = []
        gui_exprs = []
        for sub_idx, sub_expr in enumerate(sub_exprs):
            sub_name = get_key_str(expr=sub_expr, key=ExprKeys.FIELD, valid=field_subs)
            sub_field = field_subs[sub_name]
            operator = self._get_operator(expr=sub_expr, field=sub_field)

            sub_aql_expr, parsed_value, expr_value = self._value_parser(
                expr=sub_expr, field=sub_field, operator=operator
            )
            sub_expr_gui = GuiExpr.get_child(
                aql=sub_aql_expr,
                field=sub_field["name"],
                op_comp=operator.name_map.op,
                value=expr_value,
                idx=sub_idx,
            )

            self._aql_log(f"Complex sub-field AQL produced: {sub_aql_expr}")
            self._expr_log(
                f"Complex sub-field GUI expr produced:\n{json_dump(sub_expr_gui)}"
            )

            aqls.append(sub_aql_expr)
            gui_exprs.append(sub_expr_gui)

        aqls = [x for x in aqls if x]
        gui_exprs = [x for x in gui_exprs if x]

        aql = f" {Templates.AND} ".join([x for x in aqls if x])
        aql = Templates.COMPLEX.format(field=field["name"], aqls=aql)
        aql = GuiExpr.aql_add_logic(
            or_flag=or_flag, not_flag=not_flag, aql=aql, idx=idx, bracket=bracket,
        )

        gui_expr = GuiExpr.get_complex(
            aql=aql,
            field=field["name"],
            field_type=field["expr_field_type"],
            children=gui_exprs,
            not_flag=not_flag,
            or_flag=or_flag,
            idx=idx,
            **bracket or {},
        )

        self._aql_log(f"Complex AQL produced: {aql}")
        self._expr_log(f"Complex GUI expr produced:\n{json_dump(gui_expr)}")

        return aql, [gui_expr]

    def _handle_bracket(self, expr: dict, idx: int) -> Tuple[str, List[dict]]:
        sub_exprs = get_key_lod(expr=expr, key=ExprKeys.SUBS)
        self._parse_log(f"Parsing {len(sub_exprs)} bracket sub-exprs")

        aqls = []
        gui_exprs = []
        valid = ExprTypes.get_bracket_types()

        for sub_idx, sub_expr in enumerate(sub_exprs):
            left: bool = sub_idx == 0
            right: bool = sub_idx == len(sub_exprs) - 1
            weight: int = sub_idx - 1

            bracket = {
                ExprKeys.BRACKET_LEFT: left,
                ExprKeys.BRACKET_RIGHT: right,
                ExprKeys.BRACKET_WEIGHT: weight,
            }

            expr_type = self._get_type(expr=sub_expr, valid=valid)
            expr_method = getattr(self, f"_handle_{expr_type}")

            try:
                expr_aql, exprs_gui = expr_method(
                    expr=sub_expr, idx=sub_idx + idx, bracket=bracket
                )
            except Exception as exc:
                lines = get_expr_lines(expr=sub_expr)
                expr_idx = f"bracket expression #{idx} in sub-expression #{sub_idx}"
                msg = f"Error in {expr_idx}: {exc}\n\n{lines}"
                if self._error_stop:
                    raise WizardError(msg)
                self.LOG.exception(msg)
                continue

            aqls.append(expr_aql)
            gui_exprs += exprs_gui

        aqls = [x for x in aqls if x]
        gui_exprs = [x for x in gui_exprs if x]

        aql = " ".join(aqls)
        self._aql_log(f"Bracket AQL produced: {aql}")
        return aql, gui_exprs

    def _get_type(self, expr: dict, valid: List[str]) -> str:
        return get_key_str(
            expr=expr, key=ExprKeys.TYPE, valid=valid, default=ExprKeyDefaults.TYPE
        )

    def _get_operator(self, expr: dict, field: dict) -> Operator:
        if ExprKeys.OP not in expr:
            if ExprKeys.VALUE in expr:
                value = ExprKeyDefaults.OP_VALUE
            else:
                value = ExprKeyDefaults.OP_NO_VALUE
        else:
            value = get_key_str(expr=expr, key=ExprKeys.OP)
        return OperatorTypeMaps.get_operator(field=field, operator=value)

    def _get_or_flag(self, expr: dict) -> str:
        return get_key_bool(expr=expr, key=ExprKeys.OR, default=ExprKeyDefaults.OR)

    def _get_not_flag(self, expr: dict) -> str:
        return get_key_bool(expr=expr, key=ExprKeys.NOT, default=ExprKeyDefaults.NOT)

    def _get_field(self, expr: dict, is_complex: bool = False) -> dict:
        value = get_key_str(expr=expr, key=ExprKeys.FIELD)
        field = self.apiobj.fields.get_field_name(
            value=value,
            fields_map=self._get_api_fields(),
            key=None,
            custom_fields_map=CUSTOM_FIELDS_MAP,
        )
        fname = field["name"]
        aname = field["adapter_name"]

        if fname == ALL_NAME:
            raise ToolsError(f"Can not use field {fname!r} in queries")

        if is_complex and not field["is_complex"]:
            afields = self._get_api_fields()[aname]
            schemas = [x for x in afields if x["is_complex"] and x["name"] != ALL_NAME]
            msg = [
                f"Invalid complex field {fname!r} for {aname}, valids:",
                *self.apiobj.fields._prettify_schemas(schemas=schemas),
            ]
            raise ToolsError("\n".join(msg))

        return field

    def _value_parser(
        self, expr: dict, field: dict, operator: Operator
    ) -> Tuple[str, str, Any]:
        parser = f"_value_{operator.parser.name}"
        method = getattr(self, parser, None)
        parsed_value, expr_value = method(expr=expr, field=field)
        aql = operator.template.format(field=field["name"], parsed_value=parsed_value)
        return aql, parsed_value, expr_value

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
            raise ToolsError(f"invalid choice {value!r}, valid choices:{valid}")

        if isinstance(enum, dict):
            for item, item_value in enum.items():
                item_check = item.lower() if isinstance(item, str) else item
                value_check = value.lower() if isinstance(value, str) else value
                if item_check == value_check:
                    return item_value

            valid = "\n - " + "\n - ".join([str(x) for x in enum])
            raise ToolsError(f"invalid choice {value!r}, valid choices:{valid}")

        etype = type(enum).__name__
        raise ToolsError(f"Unhandled enum type {etype}: {enum}")

    def _value_to_str(self, expr: dict, field: dict) -> Tuple[str, str]:
        parsed_value = get_key_str(expr=expr, key=ExprKeys.VALUE)
        parsed_value = self._check_enum(value=parsed_value, field=field)
        expr_value = parsed_value
        return parsed_value, expr_value

    def _value_to_int(self, expr: dict, field: dict) -> Tuple[str, Union[int, float]]:
        value = expr.get(ExprKeys.VALUE, "")
        expr_value = coerce_int_float(value=value)
        expr_value = self._check_enum(value=expr_value, field=field)
        parsed_value = str(expr_value)
        return parsed_value, expr_value

    def _value_none(self, expr: dict) -> Tuple[str, None]:
        parsed_value = ""
        expr_value = None
        return parsed_value, expr_value

    def _value_to_raw_version(self, expr: dict, field: dict) -> Tuple[str, str]:
        expr_value = get_key_str(expr=expr, key=ExprKeys.VALUE)
        parsed_value = get_raw_version(value=expr_value)
        return parsed_value, expr_value

    def _value_to_dt(self, expr: dict, field: dict) -> Tuple[str, str]:
        parsed_value = get_key_str(expr=expr, key=ExprKeys.VALUE)
        parsed_value = dt_parse_tmpl(obj=parsed_value)
        expr_value = parsed_value
        return parsed_value, expr_value

    def _value_to_ip(self, expr: dict, field: dict) -> Tuple[str, str]:
        parsed_value = get_key_str(expr=expr, key=ExprKeys.VALUE)
        parsed_value = str(parse_ip_address(value=parsed_value))
        expr_value = parsed_value
        return parsed_value, expr_value

    def _value_to_subnet(self, expr: dict, field: dict) -> Tuple[str, str]:
        parsed_value = get_key_str(expr=expr, key=ExprKeys.VALUE)
        parsed_value = str(parse_ip_network(value=parsed_value))
        expr_value = parsed_value
        return parsed_value, expr_value

    def _value_ip_to_subnet_start_end(
        self, expr: dict, field: dict
    ) -> Tuple[List[str], str]:
        value = get_key_str(expr=expr, key=ExprKeys.VALUE)
        ip_network = parse_ip_network(value=value)
        parsed_value = [
            str(int(ip_network.network_address)),
            str(int(ip_network.broadcast_address)),
        ]
        expr_value = str(ip_network)
        return parsed_value, expr_value

    def _value_to_escaped_regex(self, expr: dict, field: dict) -> Tuple[str, str]:
        expr_value = get_key_str(expr=expr, key=ExprKeys.VALUE)
        parsed_value = re.escape(expr_value)
        return parsed_value, expr_value

    def _value_to_str_tags(self, expr: dict, field: dict) -> Tuple[str, str]:
        parsed_value = get_key_str(expr=expr, key=ExprKeys.VALUE)
        parsed_value = self._check_enum(
            value=parsed_value, field=field, extra=self._get_api_tags()
        )
        expr_value = parsed_value
        return parsed_value, expr_value

    def _value_to_str_adapters(self, expr: dict, field: dict) -> Tuple[str, str]:
        parsed_value = get_key_str(expr=expr, key=ExprKeys.VALUE)
        parsed_value = self._check_enum(
            value=parsed_value, field=field, extra=self._get_api_adapter_names()
        )
        expr_value = parsed_value
        return parsed_value, expr_value

    def _value_to_str_cnx_label(self, expr: dict, field: dict) -> str:
        parsed_value = get_key_str(expr=expr, key=ExprKeys.VALUE)
        parsed_value = self._check_enum(
            value=parsed_value, field=field, extra=self._get_api_adapter_cnx_labels()
        )
        expr_value = parsed_value
        return parsed_value, expr_value

    def _value_to_csv(
        self,
        expr: dict,
        field: dict,
        converter: Optional[Any] = None,
        join_tmpl: str = '"{}"',
        enum_extra: Optional[List[Union[int, str]]] = None,
    ) -> Tuple[str, str]:
        value = expr.get(ExprKeys.VALUE, "")
        items = coerce_str_to_csv(value=value)

        new_items = []
        for idx, item in enumerate(items):
            item_num = idx + 1
            try:
                if converter:
                    item = converter(item)
                elif not isinstance(item, str):
                    raise ToolsError("Value must be a string")

                if not isinstance(item, str):
                    item = str(item)

                item = self._check_enum(field=field, value=item, extra=enum_extra)
                new_items.append(item)
            except Exception as exc:
                raise ToolsError(f"Error in item #{item_num} of {len(items)}: {exc}")

        parsed_value = ", ".join([join_tmpl.format(x) for x in new_items])
        expr_value = ",".join([x for x in new_items])
        return parsed_value, expr_value

    def _value_to_csv_str(self, expr: dict, field: dict) -> Tuple[str, str]:
        return self._value_to_csv(expr=expr, field=field)

    def _value_to_csv_int(self, expr: dict, field: dict) -> str:
        return self._value_to_csv(
            expr=expr, converter=coerce_int_float, field=field, join_tmpl="{}"
        )

    def _value_to_csv_subnet(self, expr: dict, field: dict) -> Tuple[str, str]:
        return self._value_to_csv(expr=expr, converter=parse_ip_network, field=field)

    def _value_to_csv_ip(self, expr: dict, field: dict) -> Tuple[str, str]:
        return self._value_to_csv(expr=expr, converter=parse_ip_address, field=field)

    def _value_to_csv_tags(self, expr: dict, field: dict) -> Tuple[str, str]:
        return self._value_to_csv(
            expr=expr, field=field, enum_extra=self._get_api_tags()
        )

    def _value_to_csv_adapters(self, expr: dict, field: dict) -> Tuple[str, str]:
        return self._value_to_csv(
            expr=expr, field=field, enum_extra=self._get_api_adapter_names(),
        )

    def _value_to_csv_cnx_label(self, expr: dict, field: dict) -> Tuple[str, str]:
        parsed_value = self._value_to_csv(
            expr=expr, field=field, enum_extra=self._get_api_adapter_cnx_labels(),
        )
        return parsed_value

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
