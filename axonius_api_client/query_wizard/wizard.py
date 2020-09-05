# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import logging
from typing import Any, Dict, List, Optional, Union

from ..api.assets.asset_mixin import AssetMixin
from ..constants import LOG_LEVEL_WIZARD
from ..data_classes.wizard import (EntryKey, EntryKeys, EntryType, EntryTypes,
                                   ExprKeys, SavedQuery, Templates)
from ..exceptions import WizardError
from ..logs import get_obj_log
from ..tools import check_empty, check_type, join_kv
from .entry import (ComplexEntry, ComplexSubEntry, Entry, SavedQueryEntry,
                    SimpleEntry)


def kv_dump(obj):
    return "\n  ".join(join_kv(obj=obj, tmpl="{k}: {v}"))


class Wizard:
    def __init__(
        self, apiobj: AssetMixin, log_level: Union[str, int] = LOG_LEVEL_WIZARD
    ):
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        self.apiobj = apiobj
        self._pre_parse()
        self._cache = {}

    def parse(self, entries: List[dict]) -> List[dict]:
        check_type(value=entries, exp=(list, tuple), name="entries", exp_items=dict)
        check_empty(value=entries, name="entries")
        self._pre_parse()
        self._parse_entries(entries=entries)
        return self._sqs_serialize

    def _parse_entries(
        self, entries: List[dict], sq: Optional[SavedQuery] = None
    ) -> List[dict]:
        for idx, entry in enumerate(entries):
            src = f"from dictionary #{idx + 1}\n{kv_dump(entry)}"
            src = entry.pop("_source", src)

            try:
                self._get_entry_type(entry=entry, sq=sq)
                # self._parse_entry(entry=entry)
            except Exception as exc:
                raise WizardError(f"Error parsing entry {src}\n{exc}")

    def _get_entry_type(self, entry: dict, sq: Optional[SavedQuery] = None):
        sq_type = EntryTypes.SAVED_QUERY
        type_name = self._get_entry_key(entry, EntryKeys.TYPE)
        entry_type = self.get_entry_type(type_name)
        is_sq = entry_type == sq_type

        if not sq and not is_sq:
            raise Exception(f"First entry must be type={sq_type.name}")

        return entry_type

    def _parse_entry(self, entry: dict, sq_required: bool = False):
        type_name = self._get_entry_key(entry, EntryKeys.TYPE)
        entry_type = self.get_entry_type(type_name)
        entry_type_parser = self._type_parser_map[entry_type.name]
        entry_parser = entry_type_parser(wizard=self)
        entry_parser.parse(entry=entry, sq_required=sq_required)

    @property
    def _sqs_serialize(self):
        return [self._sq_serialize(x) for x in self.sqs]

    def _sq_serialize(self, sq: SavedQuery) -> dict:
        value = sq.to_dict()

        value["query"] = " ".join([x for x in value["query"] or [] if x.strip()])
        exprs = value["expressions"] or []

        found_left = False
        found_right = False

        for idx, expr in enumerate(exprs):
            expr[ExprKeys.IDX] = idx

            is_left = expr[ExprKeys.BRACKET_LEFT]
            is_right = expr[ExprKeys.BRACKET_RIGHT]
            children = expr[ExprKeys.CHILDREN]
            is_complex = expr.get(ExprKeys.CONTEXT) == ExprKeys.CONTEXT_OBJ

            if is_left:
                found_left = True

            if is_right:
                found_right = True

            for sub_idx, sub_expr in enumerate(children):
                sub_expr[ExprKeys.IDX] = sub_idx

            if is_complex:
                expr[ExprKeys.FILTER] = self._build_complex_query(expr=expr)

        if found_left and not found_right:
            expr = exprs[-1]
            expr[ExprKeys.BRACKET_RIGHT] = True
            expr[ExprKeys.FILTER] += ")"
            value["query"] += ")"

        return {k: v for k, v in value.items() if v not in [None, [], ""]}

    def _build_complex_query(self, expr: dict, idx: int) -> str:
        is_left = expr[ExprKeys.BRACKET_LEFT]
        is_not = expr[ExprKeys.NOT]
        is_or = expr[ExprKeys.OP_LOGIC] == Templates.OP_LOGIC_OR
        field = expr[ExprKeys.FIELD]
        children = expr[ExprKeys.CHILDREN]

        sub_queries = [x[ExprKeys.CONDITION] for x in children]
        sub_queries = [x for x in sub_queries if x]

        if not sub_queries:
            raise WizardError(f"No sub-fields defined for complex field {field}")

        sub_queries = f" {Templates.AND} ".join(sub_queries)
        query = Templates.COMPLEX.format(field=field, sub_queries=sub_queries)
        query = self._build_query_logic(
            query=query, idx=idx, is_left=is_left, is_not=is_not, is_or=is_or
        )
        return query

    def _get_entry_key(self, entry: dict, key: EntryKey) -> Any:
        return entry.get(key.name, key.default)

    @staticmethod
    def _build_query_logic(
        query: str,
        idx: int = 0,
        is_left: bool = False,
        is_right: bool = False,
        is_not: bool = False,
        is_or: bool = False,
    ) -> str:
        if is_left:
            query = Templates.LEFT_BRACKET.format(query=query)

        if is_right:
            query = Templates.RIGHT_BRACKET.format(query=query)

        if is_not:
            query = Templates.NOT_PRE.format(query=query)

        if idx:
            if is_or:
                query = Templates.OR_PRE.format(query=query)
            else:
                query = Templates.AND_PRE.format(query=query)
        return query

    @property
    def _type_parser_map(self) -> Dict[str, Entry]:
        return {
            EntryTypes.SIMPLE.name: SimpleEntry,
            EntryTypes.COMPLEX.name: ComplexEntry,
            EntryTypes.COMPLEX_SUB.name: ComplexSubEntry,
            EntryTypes.SAVED_QUERY.name: SavedQueryEntry,
        }

    @classmethod
    def get_examples(cls, include_help: bool = True) -> str:
        raise NotImplementedError()

    @classmethod
    def get_example(cls, type_name: str, include_help: bool = True) -> str:
        raise NotImplementedError()

    @classmethod
    def unparse(cls, entries: List[dict]):
        raise NotImplementedError()

    @classmethod
    def entry_unparse(cls, entry: dict) -> str:
        raise NotImplementedError()

    @classmethod
    def get_entry_type(cls, entry_type: Union[str, EntryType]) -> EntryType:
        if isinstance(entry_type, EntryType):
            return entry_type

        entry_type = entry_type.lower().strip()
        valid = {x.name: x for x in EntryTypes.get_values()}

        if entry_type not in valid:
            valid = ", ".join(list(valid))
            examples = cls.get_examples(include_help=False)
            raise WizardError(
                f"Invalid type supplied {entry_type!r}, valid choices: {valid}"
                f"\n{examples}"
            )

        return valid[entry_type]

    # XXX types
    @property
    def in_complex_no_subs(self):
        return self.in_complex and not self.complex_subs

    def _reset_bracket(self):
        self.in_bracket = False
        self.idx_bracket = 0

    def _reset_complex(self):
        self.idx_complex_sub = 0
        self.in_complex = {}
        self.complex_subs = []

    def _reset(self):
        self._reset_bracket()
        self._reset_complex()
        self.idx_expression = 0

    def _pre_parse(self):
        self._reset()
        self.sqs: List[SavedQuery] = []
        self.sq: SavedQuery = None

    def new_sq(self):
        self._reset()
        self.sq = SavedQuery()
        self.sqs.append(self.sq)

    def _fields_map(self) -> Dict[str, List[dict]]:
        return self._cache.get("fields_map", self.apiobj.fields.get())

    def _tags(self) -> List[str]:
        return self._cache.get("labels", self.apiobj.labels.get())

    def _adapters(self) -> List[dict]:
        return self._cache.get("adapters", self.apiobj.adapters.get())

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
