# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import abc
import re
from typing import Any, List, Optional, Tuple, Union

from ..constants import ALL_NAME
from ..data_classes.fields import CUSTOM_FIELDS_MAP, Operator, OperatorTypeMaps
from ..data_classes.wizard import (EntryKey, EntryKeys, EntryType, EntryTypes,
                                   ExprKeys, Templates)
from ..exceptions import WizardError
from ..tools import (check_empty, check_type, coerce_bool, coerce_int_float,
                     coerce_str_to_csv, dt_parse_tmpl, get_raw_version,
                     parse_ip_address, parse_ip_network)


class Entry(metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def entry_type(self) -> EntryType:
        pass

    @abc.abstractmethod
    def handle(self):
        pass

    def __init__(self, wizard):
        self.wizard = wizard

    def parse(self, entry: dict, sq_required: bool = False,) -> dict:
        self.sq_required: bool = sq_required
        self.entry_orig: dict = entry
        self.entry: dict = {}
        self.set_sq()

        for key in self.entry_type.keys:
            try:
                self.entry[key.name] = self.parse_key(entry=entry, key=key)
            except Exception as exc:
                example = self.wizard.get_example(self.entry_type)
                raise WizardError(
                    f"While parsing key {key.name!r}\nError: {exc}\n\n{example}"
                )

        try:
            self.handle()
        except Exception as exc:
            example = self.wizard.get_example(self.entry_type)
            raise WizardError(f"While handling entry\nError: {exc}\n\n{example}")

    def set_sq(self):
        if not self.wizard.sq:
            if self.sq_required:
                raise WizardError("need a saved query entry first")  # XXX
            self.wizard.new_sq()

    def entry_key(self, key: EntryKey) -> Any:
        return self.wizard._entry_key(entry=self.entry, key=key)

    def parse_key(self, entry: dict, key: EntryKey) -> Union[List[str], str, bool]:
        if key.name not in entry:
            if key.required:
                raise WizardError("Missing required key")

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
                raise WizardError(f"Invalid list type {vtype}")

        if key.value_type == "str" and not isinstance(value, str):
            vtype = type(value).__name__
            raise WizardError(f"Invalid string type {vtype}")

        if key.required and not isinstance(value, bool) and not value:
            raise WizardError(f"Empty value {value!r} for required key")

        if key.choices:
            value = value.lower().strip()
            if value not in key.choices:
                valid = "\n - " + "\n - ".join(key.choices)
                raise WizardError(f"Invalid choice {value!r}, valids: {valid}")

        return value

    def set_brackets(self):
        if self.is_left:
            if self.wizard.in_bracket:
                raise WizardError(
                    "Can not start a left bracket, left bracket already started"
                )
            self.wizard.in_bracket = True
            self.wizard.bracket_idx = 0

        if self.is_right:
            if not self.wizard.in_bracket:
                raise WizardError(
                    "Can not start a right bracket, left bracket not started"
                )
            self.in_bracket = False

    def bump_idxs(self):
        self.wizard.idx_expression += 1
        if self.wizard.in_bracket:
            self.wizard.idx_bracket += 1
        if self.wizard.in_complex:
            self.wizard.idx_complex_sub += 1

    @property
    def is_left(self) -> bool:
        return self.entry_key(EntryKeys.BRACKET) == "left"

    @property
    def is_right(self) -> bool:
        return self.entry_key(EntryKeys.BRACKET) == "right"

    @property
    def operator(self) -> Operator:
        return OperatorTypeMaps.get_operator(
            field=self.field, operator=self.entry_key(EntryKeys.OP)
        )

    @property
    def is_not(self) -> bool:
        return "not" in self.entry_key(EntryKeys.LOGIC)

    @property
    def is_or(self) -> bool:
        return "or" in self.entry_key(EntryKeys.LOGIC)

    def build_expr(self, query: str, value: Optional[Union[str, int]] = None) -> dict:
        op_logic = Templates.OP_LOGIC_IDX0
        if self.wizard.idx_expression:
            if self.is_or:
                op_logic = Templates.OP_LOGIC_OR
            else:
                op_logic = Templates.OP_LOGIC_AND

        weight = 0
        if self.wizard.in_bracket or self.is_right or self.is_left:
            weight = -1 if not self.wizard.idx_bracket else self.wizard.idx_bracket

        field_name = self.field["name"]
        field_type = self.field["expr_field_type"]

        expression = {}
        expression[ExprKeys.BRACKET_WEIGHT] = weight
        expression[ExprKeys.CHILDREN] = [self.build_expr_child()]
        expression[ExprKeys.OP_COMP] = self.operator.name_map.op
        expression[ExprKeys.FIELD] = field_name
        expression[ExprKeys.FIELD_TYPE] = field_type
        expression[ExprKeys.FILTER] = query
        expression[ExprKeys.FILTER_ADAPTERS] = None
        expression[ExprKeys.BRACKET_LEFT] = self.is_left
        expression[ExprKeys.OP_LOGIC] = op_logic
        expression[ExprKeys.NOT] = self.is_not
        expression[ExprKeys.BRACKET_RIGHT] = self.is_right
        expression[ExprKeys.VALUE] = value
        return expression

    def build_expr_child(
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

    @property
    def field(self) -> dict:
        if getattr(self, "_field", None):
            return self._field

        self._field = self.wizard.apiobj.fields.get_field_name(
            value=self.entry_key(EntryKeys.FIELD),
            fields_map=self.wizard._fields_map(),
            key=None,
            custom_fields_map=CUSTOM_FIELDS_MAP,
        )

        fname = self._field["name"]

        if fname == ALL_NAME:
            raise WizardError(f"Can not use field {fname!r} in queries")

        return self._field

    def parse_value(self) -> Tuple[str, Any]:
        parser = getattr(self, f"value_{self.operator.parser.name}")
        return parser(value=self.entry_key(EntryKeys.VALUE))
        # aql = operator.template.format(field=field["name"], aql_value=aql_value)
        # XX
        # return aql_value, value

    def value_to_str(self, value: Any) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value)
        return aql_value, aql_value

    def value_to_int(self, value: Any) -> Tuple[str, Union[int, float]]:
        value = coerce_int_float(value=value)
        value = self.check_enum(value=value)
        return str(value), value

    def value_to_none(self, value: Any) -> Tuple[str, None]:
        return "", None

    def value_to_raw_version(self, value: Any) -> Tuple[str, str]:
        aql_value = get_raw_version(value=value)
        return aql_value, value

    def value_to_dt(self, value: Any) -> Tuple[str, str]:
        aql_value = dt_parse_tmpl(obj=value)
        return aql_value, aql_value

    def value_to_ip(self, value: Any) -> Tuple[str, str]:
        aql_value = str(parse_ip_address(value=value))
        return aql_value, aql_value

    def value_to_subnet(self, value: Any) -> Tuple[str, str]:
        aql_value = str(parse_ip_network(value=value))
        return aql_value, aql_value

    def value_to_subnet_start_end(self, value: Any) -> Tuple[List[str], str]:
        ip_network = parse_ip_network(value=value)
        aql_value = [
            str(int(ip_network.network_address)),
            str(int(ip_network.broadcast_address)),
        ]
        return aql_value, str(ip_network)

    def value_to_str_escaped_regex(self, value: Any) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = re.escape(value)
        return aql_value, value

    def value_to_str_tags(self, value: Any) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value, extra=self.wizard._tags())
        return aql_value, aql_value

    def value_to_str_adapters(self, value: Any) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value, extra=self.wizard._adapter_names())
        return aql_value, aql_value

    def value_to_str_cnx_label(self, value: Any) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value, extra=self.wizard._cnx_labels())
        return aql_value, aql_value

    def value_to_csv_str(self, value: Any) -> Tuple[str, str]:
        return self.parse_csv(value=value)

    def value_to_csv_int(self, value: Any) -> Tuple[str, str]:
        return self.parse_csv(value=value, converter=coerce_int_float, join_tmpl="{}")

    def value_to_csv_subnet(self, value: Any) -> Tuple[str, str]:
        return self.parse_csv(value=value, converter=parse_ip_network)

    def value_to_csv_ip(self, value: Any) -> Tuple[str, str]:
        return self.parse_csv(value=value, converter=parse_ip_address)

    def value_to_csv_tags(self, value: Any) -> Tuple[str, str]:
        return self.parse_csv(value=value, enum_extra=self.wizard._tags())

    def value_to_csv_adapters(self, value: Any) -> Tuple[str, str]:
        return self.parse_csv(value=value, enum_extra=self.wizard._adapter_names())

    def value_to_csv_cnx_label(self, entry: dict) -> Tuple[str, str]:
        aql_value = self.parse_csv(entry=entry, enum_extra=self.wizard._cnx_labels())
        return aql_value

    def parse_csv(
        self,
        value: Any,
        converter: Optional[Any] = None,
        join_tmpl: str = '"{}"',
        enum_extra: Optional[List[Union[int, str]]] = None,
    ) -> Tuple[str, str]:
        items = coerce_str_to_csv(value=value)

        new_items = []
        for idx, item in enumerate(items):
            item_num = idx + 1
            try:
                if converter:
                    item = converter(item)
                elif not isinstance(item, str):
                    raise WizardError("Value must be a string")

                if not isinstance(item, str):
                    item = str(item)

                item = self.check_enum(value=item, extra=enum_extra)
                new_items.append(item)
            except Exception as exc:
                raise WizardError(f"Error in item #{item_num} of {len(items)}: {exc}")

        aql_value = ", ".join([join_tmpl.format(x) for x in new_items])
        value = ",".join([str(x) for x in new_items])
        return aql_value, value

    def check_enum(
        self, value: Union[int, str], extra: Optional[List[str]] = None
    ) -> Union[int, str]:
        fenum = self.field.get("enum") or []
        fitems = self.field.get("items") or {}
        fitems_enum = fitems.get("enum") or []

        enum = fitems_enum or fenum or extra or []

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


class SimpleEntry(Entry):
    @property
    def entry_type(self):
        return EntryTypes.SIMPLE

    def set_complex(self):
        if self.wizard.in_complex_no_subs:
            raise WizardError(
                "Can not start a simple entry when the previous "
                "complex entry had no complex_sub entries"
            )
        self.wizard._reset_complex()

    def handle(self):
        self.set_complex()
        self.set_brackets()
        aql_value, value = self.parse_value()
        query = self.operator.template.format(
            field=self.field["name"], aql_value=aql_value
        )
        query = self.wizard._build_query_logic(
            query=query,
            idx=self.wizard.idx_expression,
            is_left=self.is_left,
            is_right=self.is_right,
            is_not=self.is_not,
            is_or=self.is_or,
        )
        expression = self.build_expr(query=query, value=value)
        self.wizard.sq.query.append(query)
        self.wizard.sq.expressions.append(expression)
        self.bump_idxs()


class ComplexEntry(Entry):
    @property
    def entry_type(self):
        return EntryTypes.COMPLEX

    def set_complex(self):
        if self.wizard.in_complex_no_subs:
            raise WizardError(
                "Can not start a complex entry when the previous "
                "complex entry had no complex_sub entries"
            )
        self.wizard._reset_complex()
        self.wizard.in_complex = self.field

    def handle(self):
        self.set_complex()
        self.set_brackets()

    @property
    def field(self) -> dict:
        value = super().field

        if not value["is_complex"]:
            fname = value["name"]
            aname = value["adapter_name"]
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
                *self.wizard.apiobj.fields._prettify_schemas(schemas=schemas),
            ]
            raise WizardError("\n".join(msg))

        return value

    def build_expr(self) -> dict:
        expression = super().build_expr(query="")
        expression[ExprKeys.CHILDREN] = self.wizard.complex_subs
        expression[ExprKeys.OP_COMP] = ""
        expression[ExprKeys.CONTEXT] = ExprKeys.CONTEXT_OBJ
        return expression


class ComplexSubEntry(Entry):

    # def _handle_complex_sub(self):
    #     pass
    #     """
    #     if not in complex, Error
    #     need to have _complex_idx
    #     """

    @property
    def entry_type(self):
        return EntryTypes.COMPLEX_SUB

    def handle(self):
        pass

    def set_sq(self):
        pass


class SavedQueryEntry(Entry):
    @property
    def entry_type(self):
        return EntryTypes.SAVED_QUERY

    def set_sq(self):
        self.wizard.new_sq()

    def handle(self):
        self.wizard.sq.name = self.entry_key(EntryKeys.SQ_NAME)
        self.wizard.sq.description = self.entry_key(EntryKeys.SQ_DESC)
        self.wizard.sq.tags = self.entry_key(EntryKeys.SQ_TAGS)
        fields = self.entry_key(EntryKeys.SQ_FIELDS)
        fields = self.wizard.apiobj.fields.validate(
            fields=fields, fields_map=self.wizard._fields_map(), fields_default=False,
        )
        self.wizard.sq.fields_manual = fields
