# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import logging
from typing import Any, Dict, List, Optional, Union

from ..api.assets.asset_mixin import AssetMixin
from ..constants import ALL_NAME, LOG_LEVEL_WIZARD
from ..data_classes.fields import CUSTOM_FIELDS_MAP, Operator, OperatorTypeMaps
from ..data_classes.wizard import (AllEntryTypes, EntryKey, EntryKeys,
                                   EntryType, EntryTypes, ExprKeys, Templates)
from ..exceptions import WizardError
from ..logs import get_obj_log
from ..tools import check_type, coerce_bool, join_kv
from .value_parser import ValueParser


def kv_dump(obj):
    return "\n  ".join(join_kv(obj=obj, tmpl="{k}: {v}"))


class Wizard:
    def __init__(
        self, apiobj: AssetMixin, log_level: Union[str, int] = LOG_LEVEL_WIZARD
    ):
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        self.apiobj = apiobj
        self.parse_value = ValueParser(wizard=self)
        self._cache = {}

    def parse(self, entries: List[dict]) -> List[dict]:
        check_type(value=entries, exp=(list, tuple), name="entries", exp_items=dict)
        self._pre_parse(entries=entries)
        exprs = []
        for idx, entry in enumerate(entries):
            entry_type = self._get_entry_type(entry=entry, entry_types=EntryTypes)
            src = f"{entry_type.name} entry {idx + 1}/{len(entries)}"

            if "source" in entry:
                src = f"{src} from {entry['source']}"

            if entry_type == AllEntryTypes.SIMPLE:
                expr = self._parse_simple(entry=entry, idx=idx)
            if entry_type == AllEntryTypes.COMPLEX:
                expr = self._parse_complex(entry=entry, idx=idx)
            exprs.append(expr)

        query = " ".join([x[ExprKeys.FILTER] for x in exprs])
        return {"expressions": exprs, "query": query}

    def _parse_simple(self, entry: dict, idx: int):
        field = entry[EntryKeys.FIELD_SIMPLE.name]
        field = self._get_field(value=field)

        operator = entry[EntryKeys.OP_SUB.name]
        operator = self._get_operator(entry=entry, field=field, value=operator)

        value = entry[EntryKeys.VALUE_SIMPLE.name]

        aql_value, expr_value = self.parse_value(
            field=field, operator=operator, value=value,
        )

        query = operator.template.format(field=field["name"], aql_value=aql_value)

        expr = self._build_expr(
            entry=entry,
            field=field,
            idx=idx,
            value=expr_value,
            op_comp=operator.name_map.op,
            query=query,
        )

        return expr

    def _parse_complex(self, entry: dict, idx: int):
        field = entry[EntryKeys.FIELD_COMPLEX.name]
        field = self._get_field(value=field, is_complex=True)

        field_subs = {x["name"]: x for x in field["sub_fields"]}
        fname = field["name"]

        sub_entries = entry.get("subs", [])
        sub_exprs = []
        sub_queries = []

        for sub_idx, sub_entry in enumerate(sub_entries):
            sub_field = sub_entry[EntryKeys.FIELD_COMPLEX_SUB.name]

            if sub_field not in field_subs:
                valid = list(field_subs)
                raise WizardError(
                    f"Invalid sub field {sub_field} of complex field {fname}"
                    f", valid:{valid}"
                )

            sub_field = field_subs[sub_field]

            sub_operator = sub_entry[EntryKeys.OP_SUB.name]
            sub_operator = self._get_operator(
                entry=sub_entry, field=sub_field, value=sub_operator
            )

            sub_value = sub_entry[EntryKeys.VALUE_COMPLEX_SUB.name]

            sub_aql_value, sub_expr_value = self.parse_value(
                field=sub_field, operator=sub_operator, value=sub_value,
            )

            sub_query = sub_operator.template.format(
                field=sub_field["name"], aql_value=sub_aql_value
            )

            sub_expr = self._build_expr_child(
                query=sub_query,
                op_comp=sub_operator.name_map.op,
                field=sub_field["name"],
                value=sub_expr_value,
                idx=sub_idx,
            )
            sub_queries.append(sub_expr[ExprKeys.CONDITION])
            sub_exprs.append(sub_expr)

        sub_queries = f" {Templates.AND} ".join(sub_queries)
        query = Templates.COMPLEX.format(field=fname, sub_queries=sub_queries)
        expr = self._build_expr(
            entry=entry,
            field=field,
            idx=idx,
            query=query,
            value=None,
            op_comp="",
            children=sub_exprs,
        )
        expr[ExprKeys.CONTEXT] = ExprKeys.CONTEXT_OBJ
        return expr

    def _pre_parse(self, entries: List[dict]):
        is_open = False
        weight = 0

        for idx, entry in enumerate(entries):
            entry_type = self._get_entry_type(entry=entry, entry_types=EntryTypes)
            src = f"{entry_type.name} entry {idx + 1}/{len(entries)}"

            if "source" in entry:
                src = f"{src} from {entry['source']}"

            self._parse_keys(entry=entry, entry_type=entry_type, src=src)
            self._pre_parse_complex(entry=entry, entry_type=entry_type, src=src)

            is_last = len(entries) - 1 == idx

            bracket_left = entry[EntryKeys.BRACKET_LEFT.name]
            bracket_right = entry[EntryKeys.BRACKET_RIGHT.name]

            etxt = f"entry {idx + 1}/{len(entries)}"

            if is_open:
                if bracket_left:
                    prev_idx = idx - 1
                    self.LOG.debug(
                        f"bracket is open but bracket_left=True in {etxt}, "
                        f"closing previous entry"
                    )
                    entries[prev_idx][EntryKeys.BRACKET_RIGHT.name] = True

                if not bracket_right and is_last:
                    self.LOG.debug(
                        "bracket is open but last entry bracket_right=False, "
                        "closing last entry"
                    )
                    entry[EntryKeys.BRACKET_RIGHT.name] = True

                weight += 1
                entry["bracket_weight"] = weight

            if entry[EntryKeys.BRACKET_LEFT.name]:
                entry["bracket_weight"] = -1
                weight = 0
                is_open = True

            if entry[EntryKeys.BRACKET_RIGHT.name]:
                is_open = False

    def _parse_keys(self, entry: dict, entry_type: EntryType, src: str):
        # XXXX check dict type
        for key in entry_type.keys:
            try:
                entry[key.name] = self._parse_key(entry=entry, key=key)
            except Exception as exc:
                example = self.get_example(entry_type=entry_type)
                err = f"Error parsing key {key.name!r} in {src}"
                raise WizardError(f"{err}\n{exc}{example}")
        return entry

    def _parse_key(self, entry: dict, key: EntryKey) -> Any:
        if key.name not in entry:
            if key.required:
                raise WizardError(f"Missing required key {key.name!r}")

            value = key.default
        else:
            value = entry[key.name]

        if key.value_type == "bool":
            value = coerce_bool(obj=value)

        if key.value_type == "csv":
            if isinstance(value, str):
                value = [x.strip() for x in value.split(",") if x.strip()]

            if not isinstance(value, (list, tuple)) and value is not None:
                vtype = type(value).__name__
                raise WizardError(f"Invalid list type {vtype} for key {key.name!r}")

        if key.value_type == "str" and not isinstance(value, str):
            vtype = type(value).__name__
            raise WizardError(f"Invalid string type {vtype} for key {key.name!r}")

        if key.required and key.value_type == "bool" and not value:
            raise WizardError(f"Empty value {value!r} for required key {key.name!r}")

        if key.choices:
            value = value.lower().strip()
            if value not in key.choices:
                valid = "\n - " + "\n - ".join(key.choices)
                raise WizardError(
                    f"Invalid choice {value!r} for key {key.name!r}, valids: {valid}"
                )

        return value

    def _pre_parse_complex(self, entry: dict, entry_type: EntryTypes, src: str):
        if entry_type == EntryTypes.COMPLEX:
            sub_entries = entry.get("subs", [])

            if not isinstance(sub_entries, (list, tuple)) or not sub_entries:
                raise WizardError("No sub fields defined!")

            for sub_idx, sub_entry in enumerate(sub_entries):
                sub_src = f"sub-field entry {sub_idx + 1}/{len(sub_entries)}"
                if "source" in sub_entry:
                    sub_src = f"{sub_src} from {sub_entry['source']}"

                self._parse_keys(
                    entry=sub_entry, entry_type=AllEntryTypes.COMPLEX_SUB, src=src
                )

    def _build_expr(
        self,
        entry: dict,
        query: str,
        field: dict,
        idx: int,
        value: str,
        op_comp: str,
        children: Optional[List[dict]] = None,
    ) -> dict:
        bracket_right = entry[EntryKeys.BRACKET_RIGHT.name]
        bracket_left = entry[EntryKeys.BRACKET_LEFT.name]
        bracket_weight = entry["bracket_weight"]
        is_not = entry[EntryKeys.NOT.name]
        is_or = entry[EntryKeys.OR.name]

        if bracket_right:
            query = Templates.BRACKET_RIGHT.format(query=query)

        if bracket_left:
            query = Templates.BRACKET_LEFT.format(query=query)

        if is_not:
            query = Templates.NOT_PRE.format(query=query)

        if idx:
            if is_or:
                query = Templates.OR_PRE.format(query=query)
                op_logic = Templates.OP_LOGIC_OR
            else:
                query = Templates.AND_PRE.format(query=query)
                op_logic = Templates.OP_LOGIC_AND
        else:
            op_logic = Templates.OP_LOGIC_IDX0

        expression = {}
        expression[ExprKeys.BRACKET_WEIGHT] = bracket_weight
        expression[ExprKeys.CHILDREN] = children or [self._build_expr_child()]
        expression[ExprKeys.OP_COMP] = op_comp
        expression[ExprKeys.FIELD] = field["name"]
        expression[ExprKeys.FIELD_TYPE] = field["expr_field_type"]
        expression[ExprKeys.FILTER] = query
        expression[ExprKeys.FILTER_ADAPTERS] = None
        expression[ExprKeys.BRACKET_LEFT] = bracket_right
        expression[ExprKeys.OP_LOGIC] = op_logic
        expression[ExprKeys.NOT] = is_not
        expression[ExprKeys.BRACKET_RIGHT] = bracket_right
        expression[ExprKeys.VALUE] = value
        return expression

    def _build_expr_child(
        self,
        query: str = "",
        op_comp: str = "",
        field: str = "",
        value: Optional[Union[int, str]] = None,
        idx: int = 0,
    ) -> dict:
        expression = {}
        expression[ExprKeys.CONDITION] = query
        expression[ExprKeys.EXPR] = {}
        expression[ExprKeys.EXPR][ExprKeys.OP_COMP] = op_comp
        expression[ExprKeys.EXPR][ExprKeys.FIELD] = field
        expression[ExprKeys.EXPR][ExprKeys.FILTER_ADAPTERS] = None
        expression[ExprKeys.EXPR][ExprKeys.VALUE] = value
        expression[ExprKeys.IDX] = idx
        return expression

    def _get_entry_type(self, entry: dict, entry_types: EntryTypes) -> EntryType:
        value = entry.get(EntryKeys.TYPE.name, EntryKeys.TYPE.default)
        value = value.lower().strip()
        valid = {x.name: x for x in entry_types.get_values()}

        if value not in valid:
            src = entry.get("source", "")
            valid = ", ".join(list(valid))
            examples = self.get_examples(include_help=False)
            raise WizardError(
                f"Error in {src}\nInvalid type {value!r}, choices: {valid}"
                f"\n{examples}"
            )

        return valid[value]

    def _get_operator(self, entry: dict, value: str, field: dict) -> Operator:
        return OperatorTypeMaps.get_operator(field=field, operator=value)

    def _get_field(self, value: str, is_complex: bool = False):
        field = self.apiobj.fields.get_field_name(
            value=value,
            fields_map=self._fields_map(),
            key=None,
            custom_fields_map=CUSTOM_FIELDS_MAP,
        )

        fname = field["name"]

        if fname == ALL_NAME:
            raise WizardError(f"Can not use field {fname!r} in queries")

        if is_complex and not field["is_complex"]:
            fname = field["name"]
            aname = field["adapter_name"]
            afields = self.wizard._fields_map()[aname]
            schemas = [
                x
                for x in afields
                if x["is_complex"]
                and x["name"] != ALL_NAME
                and not x["name"].endswith("_details")
            ]
            msg = [
                f"Invalid complex field {fname!r} for adapter {aname!r}, valids:",
                *self.apiobj.fields._prettify_schemas(schemas=schemas),
            ]
            raise WizardError("\n".join(msg))

        return field

    def _fields_map(self) -> Dict[str, List[dict]]:
        if "fields_map" not in self._cache:
            self._cache["fields_map"] = self.apiobj.fields.get()
        return self._cache["fields_map"]

    def _tags(self) -> List[str]:
        if "labels" not in self._cache:
            self._cache["labels"] = self.apiobj.labels.get()
        return self._cache["labels"]

    def _adapters(self) -> List[dict]:
        if "adapters" not in self._cache:
            self._cache["adapters"] = self.apiobj.adapters.get()
        return self._cache["adapters"]

    def _adapter_names(self) -> Dict[str, str]:
        return {x["name"]: x["name_raw"] for x in self._adapters() if x["cnx"]}

    def _cnx_labels(self) -> List[str]:
        value = []
        for adapter in self._adapters():
            for cnx in adapter["cnx"]:
                config = cnx.get("config", {})
                label = config.get("connection_label", "")
                if label and label not in value:
                    value.append(label)
        return value
