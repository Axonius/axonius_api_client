# -*- coding: utf-8 -*-
"""Python API Client for Axonius."""
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from cachetools import TTLCache, cached

from ..api.assets.asset_mixin import AssetMixin
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

    def __call__(
        self,
        value: Any,
        parser: str,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, Any]:
        method = getattr(self, f"value_{parser}")
        try:
            return method(value=value, enum=enum, enum_items=enum_items)
        except WizardError:
            raise
        except Exception as exc:
            raise WizardError(str(exc))

    def value_to_csv_adapters(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        return self.parse_csv(
            value=value,
            enum=enum,
            enum_items=enum_items,
            enum_custom=self._adapter_names(),
            custom_id="adapter",
        )

    def value_to_csv_cnx_label(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        aql_value = self.parse_csv(
            value=value,
            enum=enum,
            enum_items=enum_items,
            enum_custom=self._cnx_labels(),
            custom_id="connection label",
        )
        return aql_value

    def value_to_csv_int(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        return self.parse_csv(
            value=value,
            enum=enum,
            enum_items=enum_items,
            converter=coerce_int_float,
            join_tmpl="{}",
        )

    def value_to_csv_ip(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        return self.parse_csv(
            value=value, enum=enum, enum_items=enum_items, converter=parse_ip_address
        )

    def value_to_csv_str(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        return self.parse_csv(value=value, enum=enum, enum_items=enum_items)

    def value_to_csv_subnet(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        return self.parse_csv(
            value=value, enum=enum, enum_items=enum_items, converter=parse_ip_network
        )

    def value_to_csv_tags(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        return self.parse_csv(
            value=value,
            enum=enum,
            enum_items=enum_items,
            enum_custom=self._tags(),
            custom_id="tag",
        )

    def value_to_dt(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        aql_value = dt_parse_tmpl(obj=value)
        return aql_value, aql_value

    def value_to_in_subnet(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[List[str], str]:
        ip_network = parse_ip_network(value=value)
        aql_value = [
            str(int(ip_network.network_address)),
            str(int(ip_network.broadcast_address)),
        ]
        return aql_value, str(ip_network)

    def value_to_int(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, Union[int, float]]:
        value = coerce_int_float(value=value)
        value = self.check_enum(value=value, enum=enum, enum_items=enum_items)
        return str(value), value

    def value_to_ip(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        aql_value = str(parse_ip_address(value=value))
        return aql_value, aql_value

    def value_to_none(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, None]:
        return "", None

    def value_to_raw_version(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        aql_value = get_raw_version(value=value)
        return aql_value, value

    def value_to_str(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value, enum=enum, enum_items=enum_items)
        return aql_value, aql_value

    def value_to_str_adapters(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(
            value=value,
            enum=enum,
            enum_items=enum_items,
            enum_custom=self._adapter_names(),
            custom_id="adapter",
        )
        return aql_value, aql_value

    def value_to_str_cnx_label(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(
            value=value,
            enum=enum,
            enum_items=enum_items,
            enum_custom=self._cnx_labels(),
            custom_id="connection label",
        )
        return aql_value, aql_value

    def value_to_str_escaped_regex(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = re.escape(value)
        return aql_value, value

    def value_to_str_tags(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(
            value=value,
            enum=enum,
            enum_items=enum_items,
            enum_custom=self._tags(),
            custom_id="tag",
        )
        return aql_value, aql_value

    def value_to_str_subnet(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        aql_value = str(parse_ip_network(value=value))
        return aql_value, aql_value

    def parse_csv(
        self,
        value: Any,
        converter: Optional[Any] = None,
        join_tmpl: str = '"{}"',
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
        enum_custom: Optional[List[Union[int, str]]] = None,
        custom_id: Optional[str] = None,
    ) -> Tuple[str, str]:
        items = coerce_str_to_csv(value=value)

        new_items = []
        for idx, item in enumerate(items):
            item_num = idx + 1
            try:
                new_items.append(
                    self.check_enum(
                        value=converter(item) if converter else item,
                        enum=enum,
                        enum_items=enum_items,
                        enum_custom=enum_custom,
                        custom_id=custom_id,
                    )
                )
            except Exception as exc:
                raise WizardError(f"Error in item #{item_num} of {len(items)}: {exc}")

        aql_value = ", ".join([join_tmpl.format(x) for x in new_items])
        value = ",".join([str(x) for x in new_items])
        return aql_value, value

    def check_enum(
        self,
        value: Union[int, str],
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
        enum_custom: Optional[Union[List[str], Dict[str, str]]] = None,
        custom_id: Optional[str] = None,
    ) -> Union[int, str]:
        if enum_custom is not None and not enum_custom:
            raise WizardError(f"No {custom_id}s exist, can not query for {custom_id} {value!r}")

        enum = enum or enum_items or enum_custom

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

        elif isinstance(enum, dict):
            for item, item_value in enum.items():
                item_check = item.lower() if isinstance(item, str) else item
                value_check = value.lower() if isinstance(value, str) else value
                if item_check == value_check:
                    return item_value

            valid = "\n - " + "\n - ".join([str(x) for x in enum])
            raise WizardError(f"invalid choice {value!r}, valid choices:{valid}")
        else:  # pragma: no cover
            etype = type(enum).__name__
            raise WizardError(f"Unhandled enum type {etype}: {enum}")

    def _tags(self) -> List[str]:
        return self.apiobj.labels.get()

    @cached(cache=CACHE)
    def _adapters(self) -> List[dict]:
        return self.apiobj.adapters.get()

    def _adapter_names(self) -> Dict[str, str]:
        return {x["name"]: x["name_raw"] for x in self._adapters() if x["cnx"]}

    def _cnx_labels(self) -> List[str]:
        value = []
        for adapter in self._adapters():
            for cnx in adapter["cnx"]:
                config = cnx.get("config", {})
                label = config.get("connection_label", "")
                if label and label not in value:  # pragma: no cover
                    value.append(label)
        return value
