# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from cachetools import TTLCache, cached

from ..api.assets.asset_mixin import AssetMixin
from ..api.parsers.constants import Operator
from ..exceptions import WizardError
from ..tools import (
    check_empty,
    check_type,
    coerce_int_float,
    coerce_str_to_csv,
    dt_parse_tmpl,
    get_raw_version,
    parse_ip_address,
    parse_ip_network,
)

CACHE: TTLCache = TTLCache(maxsize=1024, ttl=30)


class ValueParser:
    def __init__(self, apiobj: AssetMixin):
        self.apiobj = apiobj

    def __call__(self, value: Any, field: dict, operator: Operator) -> Tuple[str, Any]:
        self.field = field
        self.operator = operator
        self.value = value

        parser = getattr(self, f"value_{operator.parser.name}")
        return parser(value=value)

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
        aql_value = self.check_enum(value=value, extra=self._tags())
        return aql_value, aql_value

    def value_to_str_adapters(self, value: Any) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value, extra=self._adapter_names())
        return aql_value, aql_value

    def value_to_str_cnx_label(self, value: Any) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value, extra=self._cnx_labels())
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
        return self.parse_csv(value=value, enum_extra=self._tags())

    def value_to_csv_adapters(self, value: Any) -> Tuple[str, str]:
        return self.parse_csv(value=value, enum_extra=self._adapter_names())

    def value_to_csv_cnx_label(self, entry: dict) -> Tuple[str, str]:
        aql_value = self.parse_csv(entry=entry, enum_extra=self._cnx_labels())
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
