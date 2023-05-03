# -*- coding: utf-8 -*-
"""Parser for query wizards."""
import re
from typing import Any, Callable, List, Optional, Tuple, Union

from cachetools import TTLCache, cached

from ..exceptions import WizardError
from ..tools import (
    check_empty,
    check_type,
    coerce_int_float,
    coerce_str_to_csv,
    dt_parse_tmpl,
    get_raw_version,
    lowish,
    parse_ip_address,
    parse_ip_network,
    strip_right,
)
from .tables import tablize

CACHE_MAXSIZE: int = 4096
CACHE_TTL: int = 30
CACHE_ADAPTERS: TTLCache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
CACHE_SQS: TTLCache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
CACHE_INSTANCES: TTLCache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
CACHE_CNX_LABELS: TTLCache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
CACHE_ASSET_LABELS: TTLCache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
CACHE_ASSET_LABELS_EXPIRABLE: TTLCache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)


class WizardParser:
    """Wizard value parsers for the various field types."""

    def __init__(self, apiobj):
        """Parse for the various field types.

        Args:
            apiobj :obj:`axonius_api_client.api.assets.asset_mixin.AssetMixin`: Asset object to
                use when validating fields/adapters/connection labels/etc.
        """
        self.apiobj = apiobj
        """:obj:`axonius_api_client.api.assets.asset_mixin.AssetMixin`: Asset object to
        use when validating fields/adapters/connection labels/etc."""

    def __call__(
        self,
        value: Any,
        parser: str,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, Any]:
        """Parse a value and return the AQL and raw expression values.

        Args:
            value: value to parse/validate as valid enum
            parser: parser from field type to use
            enum: valid values allowed for the field this value is intended for
            enum_items: more valid values allowed for the field this value is intended for

        Returns:
            AQL value and raw expression value
        """
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
        """Parse a value as a comma separated list of valid adapter names."""
        return self.parse_csv(
            value=value,
            enum=enum,
            enum_items=enum_items,
            enum_callback=self.enum_cb_adapter_name,
        )

    def value_to_csv_cnx_label(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a comma separated list of valid connection labels."""
        return self.parse_csv(value=value, enum_callback=self.enum_cb_cnx_label)

    def value_to_csv_int(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a comma separated list of integers."""
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
        """Parse a value as a comma separated list of IP addresses."""
        return self.parse_csv(
            value=value, enum=enum, enum_items=enum_items, converter=parse_ip_address
        )

    def value_to_csv_str(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a comma separated list of strings."""
        return self.parse_csv(value=value, enum=enum, enum_items=enum_items)

    def value_to_csv_subnet(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a comma separated list of subnets."""
        return self.parse_csv(
            value=value, enum=enum, enum_items=enum_items, converter=parse_ip_network
        )

    def value_to_csv_tags(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a comma separated list of valid asset tags (labels)."""
        return self.parse_csv(value=value, enum_callback=self.enum_cb_asset_tags)

    def value_to_csv_tags_expirable(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a comma separated list of valid asset tags (labels)."""
        return self.parse_csv(value=value, enum_callback=self.enum_cb_asset_tags_expirable)

    def value_to_dt(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a datetime string."""
        aql_value = dt_parse_tmpl(obj=value)
        return aql_value, aql_value

    def value_to_in_subnet(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[List[str], str]:
        """Parse a value into the start and end of a subnet."""
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
        """Parse a value as an integer."""
        value = coerce_int_float(value=value)
        value = self.check_enum(value=value, enum=enum, enum_items=enum_items)
        return str(value), value

    def value_to_ip(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as an IP address."""
        aql_value = str(parse_ip_address(value=value))
        return aql_value, aql_value

    def value_to_none(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, None]:
        """Parse a value as none."""
        return "", None

    def value_to_raw_version(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a raw version string."""
        aql_value = get_raw_version(value=value)
        return aql_value, value

    def value_to_str(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a string."""
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
        """Parse a value as a valid adapter name."""
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(
            value=value,
            enum=enum,
            enum_items=enum_items,
            enum_callback=self.enum_cb_adapter_name,
        )
        return aql_value, aql_value

    def value_to_str_sq(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a valid name or UUID of Saved Query."""
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value, enum_callback=self.enum_cb_sq)
        return aql_value, aql_value

    def value_to_str_data_scope(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a valid name or UUID of a Data Scope."""
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value, enum_callback=self.enum_cb_data_scope)
        return aql_value, aql_value

    def value_to_str_cnx_label(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a valid connection label."""
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value, enum_callback=self.enum_cb_cnx_label)
        return aql_value, aql_value

    def value_to_str_escaped_regex(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as an escaped regular expression."""
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
        """Parse a value as a valid asset tag (label)."""
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value, enum_callback=self.enum_cb_asset_tags)
        return aql_value, aql_value

    def value_to_str_tags_expirable(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a valid asset tag (label)."""
        check_type(value=value, exp=str)
        check_empty(value=value)
        aql_value = self.check_enum(value=value, enum_callback=self.enum_cb_asset_tags_expirable)
        return aql_value, aql_value

    def value_to_str_subnet(
        self,
        value: Any,
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """Parse a value as a subnet."""
        aql_value = str(parse_ip_network(value=value))
        return aql_value, aql_value

    def parse_csv(
        self,
        value: Any,
        converter: Optional[Any] = None,
        join_tmpl: str = '"{}"',
        enum: Optional[List[str]] = None,
        enum_items: Optional[List[str]] = None,
        enum_callback: Optional[Callable] = None,
    ) -> Tuple[str, str]:
        """Parse a comma separated string.

        Args:
            value: string to split
            converter: method to convert each item after split
            join_tmpl: template to use when joining the values for the SQL value
            enum: valid values allowed for the field this value is intended for
            enum_items: more valid values allowed for the field this value is intended for
            enum_callback: custom values allowed for the field this value is intended for
        """

        def parse_item(item, idx):
            try:
                return self.check_enum(
                    value=converter(item) if converter else item,
                    enum=enum,
                    enum_items=enum_items,
                    enum_callback=enum_callback,
                )
            except Exception as exc:
                raise WizardError(f"Error in item #{idx + 1} of {len(items)} from {value!r}: {exc}")

        items = coerce_str_to_csv(value=value)
        new_items = [parse_item(item=item, idx=idx) for idx, item in enumerate(items)]
        aql_value = ", ".join([join_tmpl.format(x) for x in new_items])
        value = ",".join([str(x) for x in new_items])
        return aql_value, value

    def check_enum(
        self,
        value: Union[int, str],
        enum: Optional[List[Union[str, int, float]]] = None,
        enum_items: Optional[List[Union[str, int, float]]] = None,
        enum_callback: Optional[Callable] = None,
    ) -> Union[int, str]:
        """Check that the value is a valid option of enums.

        Args:
            value: value to check
            enum: valid values allowed for the field this value is intended for
            enum_items: more valid values allowed for the field this value is intended for
            enum_callback: custom values allowed for the field this value is intended for
        """
        if callable(enum_callback):
            return enum_callback(value=value)

        enum_use = enum or enum_items or None
        value_check = lowish(value)
        valids = []

        if enum_use:
            if isinstance(enum_use, (list, tuple)) and all(
                [isinstance(x, (str, int, float)) for x in enum_use]
            ):
                for item in enum_use:
                    valid = {"Valid Values": item}
                    valids.append(valid)
                    if value_check == lowish(item):
                        return item

                err = f"Invalid value {value!r} out of {len(valids)} items"
                err_table = tablize(value=valids, err=err)
                raise WizardError(err_table)

            raise WizardError(f"Unexpected enum type: {enum_use!r}")

        return value

    def enum_cb_sq(self, value: Any) -> str:
        """Pass."""
        from ..api.json_api.saved_queries import SavedQuery

        data: List[SavedQuery] = self.get_sqs()
        value_check = lowish(value)

        for item in data:
            if value_check in lowish([item.name, item.uuid]):
                return item.uuid

        err = f"No Saved Query found with name or UUID of {value!r} out of {len(data)} items"
        err_table = tablize(value=[x.to_tablize() for x in data], err=err)
        # err_table = tablize_sqs(data=data, err=err)
        raise WizardError(err_table)

    def enum_cb_cnx_label(self, value: Any) -> str:
        """Pass."""
        data = self.get_cnx_labels()
        instances = self.get_instances()
        value_check = lowish(value)
        valids = []

        for item in data:
            label = "unknown"
            adapter = "unknown"
            node_id = "unknown"
            node_name = "unknown"

            if isinstance(item, dict):
                label = item.get("label", "unknown")
                adapter = item.get("plugin_name", "unknown")
                node_id = item.get("node_id", "unknown")

            for instance in instances:
                if node_id == instance.id:
                    node_name = instance.name
                    break

            adapter = strip_right(obj=adapter, fix="_adapter")
            valid = {"Label": label, "Adapter": adapter, "Node": node_name}
            valids.append(valid)

            if value_check == lowish(label):
                return label

        err = f"No Connection Label found with name of {value!r} out of {len(valids)} items"
        err_table = tablize(value=valids, err=err)
        raise WizardError(err_table)

    def enum_cb_asset_tags(self, value: Any) -> str:
        """Pass."""
        data = self.get_asset_tags()
        value_check = lowish(value)
        valids = []

        for item in data:
            valid = {"Tag": item}
            valids.append(valid)
            if value_check == lowish(item):
                return item

        err = f"No Asset Tag found with value of {value!r} out of {len(valids)} items"
        err_table = tablize(value=valids, err=err)
        raise WizardError(err_table)

    def enum_cb_asset_tags_expirable(self, value: Any) -> str:
        """Pass."""
        data = self.get_asset_tags_expirable()
        value_check = lowish(value)
        valids = []

        for item in data:
            valid = {"Tag": item}
            valids.append(valid)
            if value_check == lowish(item):
                return item

        err = f"No Expirable Asset Tag found with value of {value!r} out of {len(valids)} items"
        err_table = tablize(value=valids, err=err)
        raise WizardError(err_table)

    def enum_cb_adapter_name(self, value: Any) -> str:
        """Pass."""
        data = self.get_adapters()
        value_check = lowish(value)
        valids = []

        for item in data:
            clients = []
            name = "unknown"
            name_raw = "unknown"
            title = "unknown"

            if isinstance(item, dict):
                clients = item.get("clients") or []
                name = item.get("name")
                name_raw = item.get("name_raw")
                title = item.get("title")

            cnx_count = len(clients)

            if cnx_count:
                valid = {"Adapter Title": title, "Adapter Name": name, "Connections": cnx_count}
                valids.append(valid)
                if value_check in lowish([name, name_raw, title]):
                    return name_raw

        err = f"No Adapter with connections found with name of {value!r} out of {len(valids)} items"
        err_table = tablize(value=valids, err=err)
        raise WizardError(err_table)

    def enum_cb_data_scope(self, value: Any) -> str:
        """Pass."""
        return self.apiobj.data_scopes.get(value=value).uuid

    @cached(cache=CACHE_ADAPTERS)
    def get_adapters(self) -> List[dict]:
        """Get all known adapters."""
        return list(self.apiobj.adapters._get_basic().adapters.values())

    @cached(cache=CACHE_CNX_LABELS)
    def get_cnx_labels(self) -> List[dict]:
        """Get all known adapter connection labels."""
        return self.apiobj.adapters._get_labels().labels

    @cached(cache=CACHE_INSTANCES)
    def get_instances(self) -> List[object]:
        """Get all known instances/nodes."""
        return self.apiobj.instances._get()

    @cached(cache=CACHE_SQS)
    def get_sqs(self) -> List[object]:
        """Get all Saved Query objects for this asset type."""
        return self.apiobj.saved_query.get(as_dataclass=True)

    @cached(cache=CACHE_ASSET_LABELS)
    def get_asset_tags(self) -> List[str]:
        """Get all known tags (labels) of this asset type."""
        return self.apiobj.labels.get()

    @cached(cache=CACHE_ASSET_LABELS_EXPIRABLE)
    def get_asset_tags_expirable(self) -> List[str]:
        """Get all known expirable tags (labels) of this asset type."""
        return self.apiobj.labels.get_expirable_names()
