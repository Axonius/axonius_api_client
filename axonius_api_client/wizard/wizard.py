# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import logging
from typing import Any, Dict, List, Optional, Union

from cachetools import TTLCache, cached

from ..api.assets.asset_mixin import AssetMixin
from ..api.parsers.constants import CUSTOM_FIELDS_MAP, OperatorTypeMaps
from ..constants import ALL_NAME, LOG_LEVEL_WIZARD
from ..exceptions import WizardError
from ..logs import get_obj_log
from ..tools import check_type
from .constants import (AllEntryTypes, Consts, EntryKey, EntryKeys, EntryType,
                        EntryTypes, ExprKeys)
from .value_parser import ValueParser

CACHE: TTLCache = TTLCache(maxsize=1024, ttl=15)


class Wizard:
    def __init__(
        self, apiobj: AssetMixin, log_level: Union[str, int] = LOG_LEVEL_WIZARD
    ):
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        self.apiobj = apiobj
        self.parse_value = ValueParser(wizard=self)

    def parse(self, entries: List[dict]) -> List[dict]:
        check_type(value=entries, exp=(list, tuple), name="entries", exp_items=dict)
        self._pre_parse(entries=entries)
        exprs = []
        for idx, entry in enumerate(entries):
            entry_type = self._get_entry_type(entry=entry, entry_types=EntryTypes)
            src = f"{entry_type.name} entry {idx + 1}/{len(entries)}"

            if Consts.SRC in entry:
                src = f"{src} from {entry[Consts.SRC]}"

            if entry_type == AllEntryTypes.SIMPLE:
                expr = self._parse_simple(entry=entry, idx=idx)
            if entry_type == AllEntryTypes.COMPLEX:
                expr = self._parse_complex(entry=entry, idx=idx)
            exprs.append(expr)

        query = " ".join([x[ExprKeys.FILTER] for x in exprs])
        return {Consts.EXPRS: exprs, Consts.QUERY: query}

    def _split_value(self, entry: dict, entry_type: EntryType) -> List[str]:
        value = entry[EntryKeys.VALUE.name]
        split = value.split(" ", maxsplit=2)
        if len(split) != 3:
            example = entry_type.key_dict(
                value=EntryKeys.VALUE.example, entry_type=entry_type
            )
            errs = [
                f"Invalid number of values in {EntryKeys.VALUE.name}={value}"
                f"Must supply 3 items like {example} "
            ]
            raise Exception("\n".join(errs))
        field, operator, value = split
        return field.strip(), operator.strip().lower(), value.lstrip()

    def _parse_simple(self, entry: dict, idx: int) -> dict:
        field, operator, value = self._split_value(
            entry=entry, entry_type=EntryTypes.SIMPLE
        )

        field = self._get_field(value=field)
        operator = OperatorTypeMaps.get_operator(operator=operator, field=field)
        aql_value, expr_value = self.parse_value(
            field=field, operator=operator, value=value,
        )
        query = operator.template.format(field=field[Consts.FNAME], aql_value=aql_value)
        expr = self._build_expr(
            entry=entry,
            field=field,
            idx=idx,
            value=expr_value,
            op_comp=operator.name_map.op,
            query=query,
        )
        return expr

    def _parse_complex(self, entry: dict, idx: int) -> dict:
        field = entry[EntryKeys.VALUE.name]

        field = self._get_field(value=field, is_complex=True)
        field_subs = {x[Consts.FNAME]: x for x in field[Consts.FSUBS]}
        sub_exprs = []

        sub_entries = entry.get(Consts.SUBS, [])
        for sub_idx, sub_entry in enumerate(sub_entries):
            sub_field, sub_operator, sub_value = self._split_value(
                entry=sub_entry, entry_type=AllEntryTypes.COMPLEX_SUB
            )

            if sub_field not in field_subs:
                valid = list(field_subs)
                raise WizardError(
                    f"Invalid sub_field {sub_field} of complex field "
                    f"{field[Consts.FNAME]}, valid: {valid}"
                )

            sub_field = field_subs[sub_field]
            sub_operator = OperatorTypeMaps.get_operator(
                operator=sub_operator, field=sub_field
            )
            sub_aql_value, sub_expr_value = self.parse_value(
                field=sub_field, operator=sub_operator, value=sub_value,
            )
            sub_query = sub_operator.template.format(
                field=sub_field[Consts.FNAME], aql_value=sub_aql_value
            )
            sub_expr = self._build_expr_child(
                query=sub_query,
                op_comp=sub_operator.name_map.op,
                field=sub_field[Consts.FNAME],
                value=sub_expr_value,
                idx=sub_idx,
            )
            sub_exprs.append(sub_expr)

        sub_queries = [x[ExprKeys.CONDITION] for x in sub_exprs]
        sub_queries = f" {Consts.AND} ".join(sub_queries)
        query = Consts.COMPLEX_TMPL.format(
            field=field[Consts.FNAME], sub_queries=sub_queries
        )
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
        tracker = 0

        for idx, entry in enumerate(entries):
            entry_type = self._get_entry_type(entry=entry, entry_types=EntryTypes)
            src = f"{entry_type.name} entry {idx + 1}/{len(entries)}"

            if Consts.SRC in entry:
                src = f"{src} from {entry[Consts.SRC]}"

            self._parse_keys(entry=entry, entry_type=entry_type, src=src)
            self._pre_parse_complex(entry=entry, entry_type=entry_type, src=src)
            flags = entry[EntryKeys.FLAGS.name]

            msgs = [
                f"entry {idx + 1}/{len(entries)}",
                f"flags={flags}",
                f"is_open={is_open}",
                f"tracker={tracker}",
            ]

            if is_open and Consts.LEFTB in flags:
                prev_idx = idx - 1
                msgs += [
                    f"is_open=True but {Consts.LEFTB} in flags",
                    f"adding {Consts.RIGHTB} to previous entry flags",
                ]
                entries[prev_idx][EntryKeys.FLAGS.name].append(Consts.RIGHTB)

            if not is_open and Consts.RIGHTB in flags:
                entry[EntryKeys.FLAGS.name].append(Consts.LEFTB)
                entry[Consts.WEIGHT] = -1
                tracker = 0
                msgs += [
                    f"is_open=False but {Consts.RIGHTB} in flags",
                    f"adding {Consts.LEFTB} to this entries flags",
                    "set final weight=-1",
                    "set tracker=0",
                ]

            if is_open:
                tracker += 1
                entry[Consts.WEIGHT] = tracker
                msgs += ["increment tracker", f"set weight={tracker}"]

            if not is_open and Consts.LEFTB not in flags:
                msgs += ["set final weight=0"]
                entry[Consts.WEIGHT] = 0

            if Consts.LEFTB in flags:
                msgs += ["set weight=-1", "set tracker=0", "set is_open=True"]
                entry[Consts.WEIGHT] = -1
                tracker = 0
                is_open = True

            if Consts.RIGHTB in flags:
                msgs += ["set is_open=False"]
                is_open = False

            msgs.append(f"final weight={entry[Consts.WEIGHT]}")
            self.LOG.debug(", ".join(msgs))

        if is_open and Consts.RIGHTB not in flags:
            msgs = [
                "last entry but bracket is left open",
                f"adding {Consts.RIGHTB} to last entries flags",
            ]
            self.LOG.debug(", ".join(msgs))
            entry[EntryKeys.FLAGS.name].append(Consts.RIGHTB)

    def _pre_parse_complex(self, entry: dict, entry_type: EntryTypes, src: str):
        if entry_type != AllEntryTypes.COMPLEX:
            return

        sub_entries = entry.get(Consts.SUBS, [])

        if not isinstance(sub_entries, (list, tuple)) or not sub_entries:
            raise WizardError("No sub fields defined!")

        for sub_idx, sub_entry in enumerate(sub_entries):
            sub_src = f"sub-field entry {sub_idx + 1}/{len(sub_entries)}"
            if Consts.SRC in sub_entry:
                sub_src = f"{sub_src} from {sub_entry[Consts.SRC]}"

            self._parse_keys(
                entry=sub_entry, entry_type=AllEntryTypes.COMPLEX_SUB, src=src
            )

    def _parse_keys(self, entry: dict, entry_type: EntryType, src: str) -> dict:
        for key in entry_type.keys:
            try:
                entry[key.name] = self._parse_key(
                    entry=entry, key=key, entry_type=entry_type
                )
            except Exception as exc:
                example = self.get_example(entry_type=entry_type)
                err = f"Error parsing key {key.name!r} from {src}\n{exc}"
                raise WizardError(f"{err}\n\n{example}\n\n{err}")
        return entry

    def _parse_key(self, entry: dict, key: EntryKey, entry_type: EntryType) -> Any:
        required = EntryType.key_dict(value=key.required, entry_type=entry_type)
        choices = EntryType.key_dict(value=key.choices, entry_type=entry_type)
        value_type = EntryType.key_dict(value=key.value_type, entry_type=entry_type)
        default = EntryType.key_dict(value=key.default, entry_type=entry_type)
        name = EntryType.key_dict(value=key.name, entry_type=entry_type)
        entry = {k.lower().strip(): v for k, v in entry.items()}

        if name not in entry:
            if required:
                raise WizardError(f"Missing required key {key.name!r}")

            value = default
        else:
            value = entry[name]

        if required and not value:
            raise WizardError(f"Empty value {value!r} for required key {name!r}")

        if value_type == Consts.TYPE_CSV:
            if isinstance(value, str):
                value = value.lstrip()
                value = [x.strip().lower() for x in value.split(",") if x.strip()]

            if not isinstance(value, (list, tuple)):
                vtype = type(value).__name__
                raise WizardError(f"Invalid list type {vtype} for key {name!r}")

            if choices:
                invalid = [x for x in value if x not in choices]
                if invalid:
                    invalid = "\n - " + "\n - ".join(invalid)
                    valid = "\n - " + "\n - ".join(list(choices))
                    errs = [
                        f"Invalid choices supplied for key {name!r}: {invalid}",
                        "",
                        f"Valid choices are: {valid}",
                    ]
                    raise WizardError("\n".join(errs))

        if value_type == Consts.TYPE_STR:
            if not isinstance(value, str):
                vtype = type(value).__name__
                raise WizardError(f"Invalid string type {vtype} for key {name!r}")

            value = value.lstrip()
            if choices:
                value = value.lower().strip()
                if value not in choices:
                    valid = "\n - " + "\n - ".join(list(choices))
                    errs = [
                        f"Invalid choice supplied for key {name!r}: {invalid}",
                        "",
                        f"valid choices are: {valid}",
                    ]
                    raise WizardError("\n".join(errs))

        return value

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
        flags = entry[EntryKeys.FLAGS.name]
        weight = entry[Consts.WEIGHT]

        is_right = Consts.RIGHTB in flags
        is_left = Consts.LEFTB in flags
        is_not = Consts.NOT in flags
        is_or = Consts.OR in flags

        if is_right:
            query = Consts.RIGHT_TMPL.format(query=query)

        if is_left:
            query = Consts.LEFT_TMPL.format(query=query)

        if is_not:
            query = Consts.NOT_TMPL.format(query=query)

        if idx:
            if is_or:
                query = Consts.OR_TMPL.format(query=query)
                op_logic = Consts.OP_LOGIC_OR
            else:
                query = Consts.AND_TMPL.format(query=query)
                op_logic = Consts.OP_LOGIC_AND
        else:
            op_logic = Consts.OP_LOGIC_IDX0

        expression = {}
        expression[ExprKeys.BRACKET_WEIGHT] = weight
        expression[ExprKeys.CHILDREN] = children or [self._build_expr_child()]
        expression[ExprKeys.OP_COMP] = op_comp
        expression[ExprKeys.FIELD] = field[Consts.FNAME]
        expression[ExprKeys.FIELD_TYPE] = field[Consts.FEXPR]
        expression[ExprKeys.FILTER] = query
        expression[ExprKeys.FILTER_ADAPTERS] = None
        expression[ExprKeys.BRACKET_LEFT] = is_left
        expression[ExprKeys.OP_LOGIC] = op_logic
        expression[ExprKeys.NOT] = is_not
        expression[ExprKeys.BRACKET_RIGHT] = is_right
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
        valid = {x.name: x for x in entry_types.get_values()}

        if EntryKeys.TYPE.name not in entry:
            src = entry.get(Consts.SRC, "")
            valid = ", ".join(list(valid))
            errs = [
                f"Error in {src}",
                f"Missing key {EntryKeys.TYPE.name!r}, valid choices: {valid}",
                self.get_examples(include_help=False),
            ]
            raise WizardError("\n".join(errs))

        value = entry.get(EntryKeys.TYPE.name, EntryKeys.TYPE.default)
        value = value.lower().strip()

        if value not in valid:
            src = entry.get(Consts.SRC, "")
            valid = ", ".join(list(valid))
            errs = [
                f"Error in {src}",
                f"Invalid {EntryKeys.TYPE.name} {value!r}, valid choices: {valid}",
                self.get_examples(include_help=False),
            ]
            raise WizardError("\n".join(errs))

        return valid[value]

    def _get_field(self, value: str, is_complex: bool = False) -> dict:
        field = self.apiobj.fields.get_field_name(
            value=value, key=None, fields_custom=CUSTOM_FIELDS_MAP,
        )

        if field[Consts.FNAME] == ALL_NAME:
            raise WizardError(f"Can not use field {field[Consts.FNAME]!r} in queries")

        if is_complex and not field["is_complex"]:
            afields = self.apiobj.fields.get()[field[Consts.FANAME]]
            schemas = [
                x
                for x in afields
                if x[Consts.FCOMPLEX]
                and x[Consts.FNAME] != ALL_NAME
                and not x[Consts.FNAME].endswith(Consts.FDETAILS)
            ]
            msg = [
                f"Invalid complex field {field[Consts.FNAME]!r} for "
                f"adapter {field[Consts.FANAME]!r}, valids:",
                *self.apiobj.fields._prettify_schemas(schemas=schemas),
            ]
            raise WizardError("\n".join(msg))

        return field

    @cached(cache=CACHE)
    def _tags(self) -> List[str]:
        return self.apiobj.labels.get()

    @cached(cache=CACHE)
    def _adapters(self) -> List[dict]:
        return self.apiobj.adapters.get()

    @cached(cache=CACHE)
    def _adapter_names(self) -> Dict[str, str]:
        return {x["name"]: x["name_raw"] for x in self._adapters() if x["cnx"]}

    @cached(cache=CACHE)
    def _cnx_labels(self) -> List[str]:
        value = []
        for adapter in self._adapters():
            for cnx in adapter["cnx"]:
                config = cnx.get("config", {})
                label = config.get("connection_label", "")
                if label and label not in value:
                    value.append(label)
        return value
