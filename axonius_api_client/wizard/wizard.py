# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import json
import logging
import pathlib
from typing import List, Optional, Tuple, Union

from ..api.assets.asset_mixin import AssetMixin
from ..api.parsers.constants import CUSTOM_FIELDS_MAP, Operator, OperatorTypeMaps
from ..constants import ALL_NAME, LOG_LEVEL_WIZARD
from ..exceptions import WizardError
from ..logs import get_obj_log
from ..tools import check_empty, check_type, listify, path_read
from .constants import (
    Checks,
    Docs,
    Entry,
    Expr,
    Fields,
    Flags,
    Results,
    Sources,
    Templates,
    Types,
)
from .value_parser import ValueParser


class Wizard:
    DOCS: str = Docs.DICT

    def __init__(
        self, apiobj: AssetMixin, log_level: Union[str, int] = LOG_LEVEL_WIZARD
    ):
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        self._apiobj: AssetMixin = apiobj
        self._value_parser: ValueParser = ValueParser(apiobj=apiobj)

    def parse(self, entries: List[dict], source: Optional[str] = None) -> List[dict]:
        source = source or Sources.LOD
        check_type(value=entries, exp=(list, tuple), exp_items=dict)
        check_empty(value=entries)
        entries = self._parse_flags(entries=entries)

        exprs = []
        for idx, entry in enumerate(entries):
            src = f"{source} entry #{idx + 1}/{len(entries)}"
            src = entry.get(Entry.SRC, src)
            try:
                expr = self._parse_entry(entry=entry, idx=idx)
            except Exception as exc:
                err = f"Error parsing from {src}:\n{exc}"
                errs = [err, self.DOCS, err]
                raise WizardError("\n".join(errs))
            exprs.append(expr)

        return {
            Results.EXPRS: exprs,
            Results.QUERY: Expr.get_query(exprs=exprs),
        }

    def parse_json(self, content: str, source: Optional[str] = None) -> List[dict]:
        source = source or Sources.JSON_STR
        entries = json.loads(content)
        return self.parse(entries=entries, source=source)

    def parse_json_path(
        self, path: Union[str, pathlib.Path], source: Optional[str] = None
    ) -> List[dict]:
        source = source or Sources.JSON_PATH.format(path=path)
        path, content = path_read(path)
        return self.parse_json(content=content, source=source)

    def _parse_entry(self, entry: dict, idx: int) -> dict:
        check_type(value=entry, exp=dict)
        check_empty(value=entry)
        self._check_keys(entry=entry, keys=Entry.REQ)
        etype = self._check_entry_type(entry=entry, types=Types.DICT)
        entry[Entry.FLAGS] = listify(entry.get(Entry.FLAGS, []))
        method = getattr(self, f"_parse_{etype}")
        return method(entry=entry, idx=idx)

    def _check_entry_type(self, entry: dict, types: List[str]) -> str:
        etype = entry[Entry.TYPE].lower().strip()
        if etype not in types:
            valid = ", ".join(types)
            raise WizardError(f"Invalid type {etype!r}, valid types: {valid}")
        return etype

    def _check_keys(self, entry: dict, keys: List[str]):
        for key in keys:
            if key not in entry:
                found = ", ".join(list(entry))
                raise WizardError(f"Missing required key {key!r}, found keys: {found}")

            value = entry[key]
            if not value:
                raise WizardError(f"Empty required key {key!r} with value {value}")

            if not isinstance(value, str):
                vtype = type(value).__name__
                raise WizardError(
                    f"Invalid type {vtype} for required key {key!r} with value {value}"
                )

    def _split_simple(self, value_raw: str) -> Tuple[str, str, str]:
        splitter = Entry.SPLIT
        split = value_raw.split(splitter, maxsplit=2)
        field = ""
        operator = ""
        value = ""

        if split:
            field = split.pop(0).strip()
            self.LOG.debug(f"Got field {field!r} from {split} from '{value_raw}'")

        if split:
            operator = split.pop(0).lower().strip()
            self.LOG.debug(f"Got operator {operator!r} from {split} from '{value_raw}'")

        if split:
            value = split.pop(0).lstrip()
            self.LOG.debug(f"Got value {value!r} from {split} from '{value_raw}'")

        self._value_checks(
            value_raw=value_raw,
            value=field,
            src="FIELD",
            checks=Checks.FIELD,
        )
        self._value_checks(
            value_raw=value_raw,
            value=operator,
            src="OPERATOR",
            checks=Checks.OP,
        )

        return field, operator, value

    def _split_complex(self, value_raw: str) -> Tuple[str, List[str]]:
        splitter = Entry.CSPLIT
        if splitter not in value_raw:
            raise WizardError(f"No {splitter} found in value '{value_raw}'")

        split = value_raw.split(splitter)
        field = ""
        subs_raw = []

        if split:
            field = split.pop(0).strip()
            self.LOG.debug(
                f"Got complex field {field!r} from {split} from '{value_raw}'"
            )

        if split:
            subs_raw = [x.lstrip() for x in split if x.lstrip()]
            self.LOG.debug(
                f"Got sub fields {subs_raw!r} from {split} from '{value_raw}'"
            )

        self._value_checks(
            value_raw=value_raw,
            value=field,
            src="FIELD",
            checks=Checks.FIELD,
        )
        self._value_checks(
            value_raw=value_raw, value=subs_raw, src="SUB-FIELD(s)", checks=[]
        )

        return field, subs_raw

    def _parse_complex(self, entry: dict, idx: int) -> dict:
        value_raw = entry[Entry.VALUE]
        field, subs_raw = self._split_complex(value_raw=value_raw)

        try:
            field = self._get_field_complex(value=field)
        except Exception as exc:
            msg = (
                f"Unable to find COMPLEX-FIELD named {field!r} from value '{value_raw}'"
            )
            raise WizardError(f"{msg}\n\n{exc}\n\n{msg}")

        sub_exprs = []
        for sub_idx, sub_raw in enumerate(subs_raw):
            try:
                sub_expr = self._parse_sub(field=field, idx=sub_idx, value_raw=sub_raw)
                sub_exprs.append(sub_expr)
            except Exception as exc:
                raise WizardError(f"Error parsing sub field from '{value_raw}'\n{exc}")

        sub_queries = Expr.get_subs_query(sub_exprs=sub_exprs)
        query = Templates.COMPLEX.format(
            field=field[Fields.NAME], sub_queries=sub_queries
        )
        expr = Expr.build(
            entry=entry,
            field=field,
            idx=idx,
            query=query,
            value=None,
            op_comp="",
            children=sub_exprs,
            is_complex=True,
        )
        return expr

    def _parse_sub(self, field: str, value_raw: str, idx: int) -> dict:
        sub_field, operator, sub_value = self._split_simple(value_raw=value_raw)

        field_subs = {x[Fields.NAME]: x for x in field[Fields.SUBS]}

        if sub_field not in field_subs:
            fname = field[Fields.NAME]
            valid = ", ".join(list(field_subs))
            err = (
                f"Unable to find SUB-FIELD named {sub_field!r} of COMPLEX field {fname}"
                f" from value '{value_raw}'\n\nValid sub_fields: {valid}"
            )
            raise WizardError(err)

        sub_field = field_subs[sub_field]
        operator = self._get_operator(
            operator=operator, field=sub_field, value_raw=value_raw
        )
        aql_value, expr_value = self._value_parser(
            field=sub_field,
            operator=operator,
            value=sub_value,
        )
        query = operator.template.format(
            field=sub_field[Fields.NAME], aql_value=aql_value
        )
        expr = Expr.build_child(
            field=sub_field[Fields.NAME],
            idx=idx,
            value=expr_value,
            op_comp=operator.name_map.op,
            query=query,
        )
        return expr

    def _parse_simple(self, entry: dict, idx: int) -> dict:
        value_raw = entry[Entry.VALUE]
        field, operator, value = self._split_simple(value_raw=value_raw)

        try:
            field = self._get_field(value=field)
        except Exception as exc:
            msg = f"Unable to find FIELD named {field!r} from value '{value_raw}'"
            raise WizardError(f"{msg}\n\n{exc}\n\n{msg}")

        operator = self._get_operator(
            operator=operator, field=field, value_raw=value_raw
        )
        aql_value, expr_value = self._value_parser(
            field=field,
            operator=operator,
            value=value,
        )
        query = operator.template.format(field=field[Fields.NAME], aql_value=aql_value)
        expr = Expr.build(
            entry=entry,
            field=field,
            idx=idx,
            value=expr_value,
            op_comp=operator.name_map.op,
            query=query,
        )
        return expr

    def _get_operator(self, operator: str, field: dict, value_raw: str) -> Operator:
        err = f"Invalid OPERATOR name {operator!r} from value '{value_raw}'\n\n"
        return OperatorTypeMaps.get_operator(operator=operator, field=field, err=err)

    def _parse_flags(self, entries: List[dict]) -> List[dict]:
        is_open = False
        tracker = 0

        for idx, entry in enumerate(entries):
            entry = self._parse_entry_flags(entry=entry)

            msgs = [
                f"entry {idx + 1}/{len(entries)}",
                f"flags={entry[Entry.FLAGS]}",
                f"is_open={is_open}",
                f"tracker={tracker}",
            ]

            if is_open and Flags.LEFTB in entry[Entry.FLAGS]:
                prev_idx = idx - 1
                msgs += [
                    f"is_open=True but {Flags.LEFTB} in flags",
                    f"adding {Flags.RIGHTB} to previous entry flags",
                ]
                entries[prev_idx][Entry.FLAGS].append(Flags.RIGHTB)

            if not is_open and Flags.RIGHTB in entry[Entry.FLAGS]:
                entry[Entry.FLAGS].append(Flags.LEFTB)
                entry[Entry.WEIGHT] = -1
                tracker = 0
                msgs += [
                    f"is_open=False but {Flags.RIGHTB} in flags",
                    f"adding {Flags.LEFTB} to this entries flags",
                    "set final weight=-1",
                    "set tracker=0",
                ]

            if is_open:
                tracker += 1
                entry[Entry.WEIGHT] = tracker
                msgs += ["increment tracker", f"set weight={tracker}"]

            if not is_open and Flags.LEFTB not in entry[Entry.FLAGS]:
                msgs += ["set final weight=0"]
                entry[Entry.WEIGHT] = 0

            if Flags.LEFTB in entry[Entry.FLAGS]:
                msgs += ["set weight=-1", "set tracker=0", "set is_open=True"]
                entry[Entry.WEIGHT] = -1
                tracker = 0
                is_open = True

            if Flags.RIGHTB in entry[Entry.FLAGS]:
                msgs += ["set is_open=False"]
                is_open = False

            msgs.append(f"final weight={entry[Entry.WEIGHT]}")
            self.LOG.debug(", ".join(msgs))

        if is_open and Flags.RIGHTB not in entry[Entry.FLAGS]:
            msgs = [
                "last entry but bracket is left open",
                f"adding {Flags.RIGHTB} to last entries flags",
            ]
            self.LOG.debug(", ".join(msgs))
            entry[Entry.FLAGS].append(Flags.RIGHTB)

        return entries

    def _parse_entry_flags(self, entry: dict) -> dict:
        value = entry[Entry.VALUE]
        flags = entry.get(Entry.FLAGS, [])

        while True:
            found = False

            for flag in Flags.FLAGS:
                value = value.lstrip()
                if value.lower().startswith(flag):
                    self.LOG.debug(f"found {flag!r} at beginning of '{value}'")
                    plen = len(flag)
                    value = value[plen:]
                    value = value.lstrip()

                    flags.append(flag)
                    found = True

            if value.lower().endswith(Flags.RIGHTB):
                self.LOG.debug(f"found {Flags.RIGHTB!r} at end of '{value}'")
                value = value[:-1]
                if value.endswith(" "):
                    value = value[:-1]

                flags.append(Flags.RIGHTB)
                found = True

            if not found:
                break

        entry[Entry.VALUE] = value
        entry[Entry.FLAGS] = flags
        return entry

    def _get_field(self, value: str) -> dict:
        field = self._apiobj.fields.get_field_name(
            value=value,
            key=None,
            fields_custom=CUSTOM_FIELDS_MAP,
        )

        if field[Fields.NAME] == ALL_NAME:
            raise WizardError(f"Can not use {ALL_NAME!r} field in queries")

        return field

    def _get_field_complex(self, value: str) -> dict:
        field = self._get_field(value=value)

        if not field[Fields.IS_COMPLEX]:
            aname = field[Fields.ANAME]
            fname = field[Fields.NAME]
            afields = self._apiobj.fields.get()[aname]
            schemas = [
                x
                for x in afields
                if x[Fields.IS_COMPLEX]
                and x[Fields.NAME] != ALL_NAME
                and not x[Fields.NAME].endswith(Fields.DETAILS)
            ]
            msg = [
                f"Invalid complex field {fname!r} for adapter {aname!r}, valids:",
                *self._apiobj.fields._prettify_schemas(schemas=schemas),
            ]
            raise WizardError("\n".join(msg))

        return field

    def _value_checks(self, value_raw: str, value: str, src: str, checks: List[str]):
        if not value:
            raise WizardError(
                f"Empty required {src} as {value!r} from value '{value_raw}'"
            )

        for check in checks:
            match = check.search(value)
            if not match:
                continue

            chars = "".join(list(match.groups()))
            raise WizardError(
                f"Using regex: {check.pattern}\n"
                f"Found invalid characters '{chars}' in {src} from value '{value}' "
                f"from '{value_raw}'"
            )
