# -*- coding: utf-8 -*-
"""Constants."""
import dataclasses
import enum
from typing import Dict, List, Optional

from ..constants import AGG_ADAPTER_NAME, AGG_ADAPTER_TITLE, AGG_EXPR_FIELD_TYPE
from ..exceptions import NotFoundError
from .base import BaseData, BaseEnum


class Parsers(BaseEnum):
    to_csv_adapters = enum.auto()
    to_csv_str = enum.auto()
    to_csv_int = enum.auto()
    to_csv_ip = enum.auto()
    to_csv_subnet = enum.auto()
    to_csv_tags = enum.auto()
    to_dt = enum.auto()
    to_escaped_regex = enum.auto()
    to_int = enum.auto()
    to_ip = enum.auto()
    to_raw_version = enum.auto()
    to_str = enum.auto()
    to_str_adapters = enum.auto()
    to_str_tags = enum.auto()
    to_subnet = enum.auto()
    ip_to_subnet_start_end = enum.auto()
    none = enum.auto()
    to_str_cnx_label = enum.auto()
    to_csv_cnx_label = enum.auto()


class Types(BaseEnum):
    string = enum.auto()
    boolean = "bool"
    integer = enum.auto()
    number = enum.auto()
    array = enum.auto()


class Formats(BaseEnum):
    datetime = "date-time"
    image = enum.auto()
    version = enum.auto()
    ip = enum.auto()
    subnet = enum.auto()
    discrete = enum.auto()
    logo = enum.auto()
    table = enum.auto()
    tag = enum.auto()
    connection_label = enum.auto()


class OperatorName(BaseData):
    name: str
    expr_name: Optional[str] = None


class OperatorNames(BaseEnum):
    contains = "contains"
    count_equals = "count_equals"
    count_less_than = "count_below"
    count_more_than = "count_above"
    endswith = "ends"
    equals = "equals"
    exists = "exists"
    is_false = "false"
    is_in = "IN"
    is_in_subnet = "subnet"
    is_ipv4 = "isIPv4"
    is_ipv6 = "isIPv6"
    is_not_in_subnet = "notInSubnet"
    is_true = "true"
    last_days = "last_days"
    last_hours = "last_hours"
    less_than = "<"
    more_than = ">"
    next_days = "next_days"
    next_hours = "next_hours"
    regex = "regex"
    startswith = "starts"


@dataclasses.dataclass
class Operator(BaseData):
    template: str
    name: OperatorNames
    parser: Parsers


def ops_clean(operators: List[Operator], clean: List[Operator]):
    return [x for x in operators if x not in clean]


@dataclasses.dataclass
class Operators(BaseData):
    contains: Operator = Operator(
        name=OperatorNames.contains,
        template='({field} == regex("{parsed_value}", "i"))',
        parser=Parsers.to_escaped_regex,
    )
    count_equals: Operator = Operator(
        name=OperatorNames.count_equals,
        template="({field} == size({parsed_value}))",
        parser=Parsers.to_int,
    )
    count_less_than: Operator = Operator(
        name=OperatorNames.count_less_than,
        template="({field} < size({parsed_value}))",
        parser=Parsers.to_int,
    )
    count_more_than: Operator = Operator(
        name=OperatorNames.count_more_than,
        template="({field} > size({parsed_value}))",
        parser=Parsers.to_int,
    )
    endswith: Operator = Operator(
        name=OperatorNames.endswith,
        template='({field} == regex("{parsed_value}$", "i"))',
        parser=Parsers.to_escaped_regex,
    )
    equals_str: Operator = Operator(
        name=OperatorNames.equals,
        template='({field} == "{parsed_value}")',
        parser=Parsers.to_str,
    )
    equals_str_tag: Operator = Operator(
        name=OperatorNames.equals,
        template='({field} == "{parsed_value}")',
        parser=Parsers.to_str_tags,
    )
    equals_str_adapter: Operator = Operator(
        name=OperatorNames.equals,
        template='({field} == "{parsed_value}")',
        parser=Parsers.to_str_adapters,
    )
    equals_str_cnx_label: Operator = Operator(
        name=OperatorNames.equals,
        template='({field} == "{parsed_value}")',
        parser=Parsers.to_str_cnx_label,
    )
    equals_ip: Operator = Operator(
        name=OperatorNames.equals,
        template='({field} == "{parsed_value}")',
        parser=Parsers.to_ip,
    )
    equals_subnet: Operator = Operator(
        name=OperatorNames.equals,
        template='({field} == "{parsed_value}")',
        parser=Parsers.to_subnet,
    )
    equals_int: Operator = Operator(
        name=OperatorNames.equals,
        template="({field} == {parsed_value})",
        parser=Parsers.to_int,
    )
    exists: Operator = Operator(
        name=OperatorNames.exists,
        template='(({field} == ({{"$exists":true,"$ne":""}})))',
        parser=Parsers.none,
    )
    exists_array: Operator = Operator(
        name=OperatorNames.exists,
        template='(({field} == ({{"$exists":true,"$ne":[]}})))',
        parser=Parsers.none,
    )
    exists_array_object: Operator = Operator(
        name=OperatorNames.exists,
        template='(({field} == ({{"$exists":true,"$ne":[]}})) and {field} != [])',
        parser=Parsers.none,
    )
    ip_in_subnet: Operator = Operator(
        name=OperatorNames.is_in_subnet,
        template=(
            '({field}_raw == match({{"$gte": {parsed_value[0]}, "$lte": '
            "{parsed_value[1]}}}))"
        ),
        parser=Parsers.ip_to_subnet_start_end,
    )
    ip_not_in_subnet: Operator = Operator(
        name=OperatorNames.is_not_in_subnet,
        template=(
            '(({field}_raw == match({{"$gte": 0, "$lte": {parsed_value[0]}}}) or '
            '{field}_raw == match({{"$gte": {parsed_value[1]}, "$lte": 4294967295}})))'
        ),
        parser=Parsers.ip_to_subnet_start_end,
    )
    ipv4: Operator = Operator(
        name=OperatorNames.is_ipv4,
        template='({field} == regex("\\."))',
        parser=Parsers.none,
    )
    ipv6: Operator = Operator(
        name=OperatorNames.is_ipv6,
        template='({field} == regex(":"))',
        parser=Parsers.none,
    )
    is_in_str: Operator = Operator(
        name=OperatorNames.is_in,
        template="({field} in [{parsed_value}])",
        parser=Parsers.to_csv_str,
    )
    is_in_str_tag: Operator = Operator(
        name=OperatorNames.is_in,
        template="({field} in [{parsed_value}])",
        parser=Parsers.to_csv_tags,
    )
    is_in_str_adapter: Operator = Operator(
        name=OperatorNames.is_in,
        template="({field} in [{parsed_value}])",
        parser=Parsers.to_csv_adapters,
    )
    is_in_str_cnx_label: Operator = Operator(
        name=OperatorNames.is_in,
        template="({field} in [{parsed_value}])",
        parser=Parsers.to_csv_cnx_label,
    )
    is_in_int: Operator = Operator(
        name=OperatorNames.is_in,
        template="{field} in [{parsed_value}]",
        parser=Parsers.to_csv_int,
    )
    is_in_ip: Operator = Operator(
        name=OperatorNames.is_in,
        template="({field} in [{parsed_value}])",
        parser=Parsers.to_csv_ip,
    )
    is_in_subnet: Operator = Operator(
        name=OperatorNames.is_in,
        template="({field} in [{parsed_value}])",
        parser=Parsers.to_csv_subnet,
    )
    is_false: Operator = Operator(
        name=OperatorNames.is_false, template="({field} == false)", parser=Parsers.none
    )
    is_true: Operator = Operator(
        name=OperatorNames.is_true, template="({field} == true)", parser=Parsers.none
    )
    last_hours: Operator = Operator(
        name=OperatorNames.last_hours,
        template='({field} >= date("NOW - {parsed_value}h"))',
        parser=Parsers.to_int,
    )
    last_days: Operator = Operator(
        name=OperatorNames.last_days,
        template='({field} >= date("NOW - {parsed_value}d"))',
        parser=Parsers.to_int,
    )
    less_than_date: Operator = Operator(
        name=OperatorNames.less_than,
        template='({field} < date("{parsed_value}"))',
        parser=Parsers.to_dt,
    )
    less_than_int: Operator = Operator(
        name=OperatorNames.less_than,
        template="({field} < {parsed_value})",
        parser=Parsers.to_int,
    )
    less_than_version: Operator = Operator(
        name=OperatorNames.less_than,
        template="({field}_raw < '{parsed_value}')",
        parser=Parsers.to_raw_version,
    )
    more_than_date: Operator = Operator(
        name=OperatorNames.more_than,
        template='({field} > date("{parsed_value}"))',
        parser=Parsers.to_dt,
    )
    more_than_int: Operator = Operator(
        name=OperatorNames.more_than,
        template="({field} < {parsed_value})",
        parser=Parsers.to_int,
    )
    more_than_version: Operator = Operator(
        name=OperatorNames.more_than,
        template="({field}_raw > '{parsed_value}')",
        parser=Parsers.to_raw_version,
    )
    next_hours: Operator = Operator(
        name=OperatorNames.next_hours,
        template='({field} >= date("NOW + {parsed_value}h"))',
        parser=Parsers.to_int,
    )
    next_days: Operator = Operator(
        name=OperatorNames.next_days,
        template='({field} >= date("NOW + {parsed_value}d"))',
        parser=Parsers.to_int,
    )
    regex: Operator = Operator(
        name=OperatorNames.regex,
        template='({field} == regex("{parsed_value}", "i"))',
        parser=Parsers.to_str,
    )
    startswith: Operator = Operator(
        name=OperatorNames.startswith,
        template='({field} == regex("^{parsed_value}", "i"))',
        parser=Parsers.to_escaped_regex,
    )


@dataclasses.dataclass
class OperatorTypeMap(BaseData):
    name: str
    operators: List[Operator]
    field_type: Types
    field_format: Optional[Formats] = None
    items_type: Optional[Types] = None
    items_format: Optional[Formats] = None


@dataclasses.dataclass
class OperatorTypeMaps(BaseData):
    string_cnx_label: OperatorTypeMap = OperatorTypeMap(
        name="string_cnx_label",
        operators=[
            Operators.exists,
            Operators.equals_str_cnx_label,
            Operators.is_in_str_cnx_label,
        ],
        field_type=Types.string,
        field_format=Formats.connection_label,
    )
    string: OperatorTypeMap = OperatorTypeMap(
        name="string",
        operators=[
            Operators.exists,
            Operators.regex,
            Operators.contains,
            Operators.equals_str,
            Operators.startswith,
            Operators.endswith,
            Operators.is_in_str,
        ],
        field_type=Types.string,
    )
    string_ip: OperatorTypeMap = OperatorTypeMap(
        name="string_ip",
        operators=[
            Operators.exists,
            Operators.regex,
            Operators.contains,
            Operators.is_in_ip,
            Operators.equals_ip,
            Operators.ip_in_subnet,
            Operators.ip_not_in_subnet,
            Operators.ipv4,
            Operators.ipv6,
        ],
        field_type=Types.string,
        field_format=Formats.ip,
    )
    string_datetime: OperatorTypeMap = OperatorTypeMap(
        name="string_datetime",
        operators=[
            Operators.exists,
            Operators.less_than_date,
            Operators.more_than_date,
            Operators.last_hours,
            Operators.next_hours,
            Operators.last_days,
            Operators.next_days,
        ],
        field_type=Types.string,
        field_format=Formats.datetime,
    )
    string_image: OperatorTypeMap = OperatorTypeMap(
        name="string_image",
        operators=[Operators.exists],
        field_type=Types.string,
        field_format=Formats.image,
    )
    string_version: OperatorTypeMap = OperatorTypeMap(
        name="string_version",
        operators=[
            Operators.exists,
            Operators.regex,
            Operators.contains,
            Operators.is_in_str,
            Operators.equals_str,
            Operators.less_than_version,
            Operators.more_than_version,
        ],
        field_type=Types.string,
        field_format=Formats.version,
    )
    string_subnet: OperatorTypeMap = OperatorTypeMap(
        name="string_subnet",
        operators=[
            Operators.exists,
            Operators.regex,
            Operators.contains,
            Operators.is_in_subnet,
            Operators.equals_subnet,
        ],
        field_type=Types.string,
        field_format=Formats.subnet,
    )
    boolean: OperatorTypeMap = OperatorTypeMap(
        name="boolean",
        operators=[Operators.is_true, Operators.is_false],
        field_type=Types.boolean,
    )
    integer: OperatorTypeMap = OperatorTypeMap(
        name="integer",
        operators=[
            Operators.exists,
            Operators.equals_int,
            Operators.is_in_int,
            Operators.less_than_int,
            Operators.more_than_int,
        ],
        field_type=Types.integer,
    )
    number: OperatorTypeMap = OperatorTypeMap(
        name="number", operators=integer.operators, field_type=Types.number,
    )
    array_object: OperatorTypeMap = OperatorTypeMap(
        name="array_object",
        operators=[Operators.exists_array_object, Operators.count_equals],
        field_type=Types.array,
        items_type=Types.array,
    )
    array_table_object: OperatorTypeMap = OperatorTypeMap(
        name="array_table_object",
        operators=array_object.operators,
        field_type=Types.array,
        field_format=Formats.table,
        items_type=Types.array,
    )
    array_integer: OperatorTypeMap = OperatorTypeMap(
        name="array_integer",
        operators=[
            Operators.exists_array,
            *ops_clean(integer.operators, [Operators.exists]),
        ],
        field_type=Types.array,
        items_type=Types.integer,
    )
    array_number: OperatorTypeMap = OperatorTypeMap(
        name="array_number",
        operators=[
            Operators.exists_array,
            *ops_clean(number.operators, [Operators.exists]),
        ],
        field_type=Types.array,
        items_type=Types.number,
    )
    array_string: OperatorTypeMap = OperatorTypeMap(
        name="array_string",
        operators=[
            Operators.exists_array,
            *ops_clean(string.operators, [Operators.exists]),
        ],
        field_type=Types.array,
        items_type=Types.string,
    )
    array_string_tag: OperatorTypeMap = OperatorTypeMap(
        name="array_string_tag",
        operators=[
            Operators.exists_array,
            Operators.count_equals,
            Operators.regex,
            Operators.contains,
            Operators.equals_str_tag,
            Operators.startswith,
            Operators.endswith,
            Operators.is_in_str_tag,
        ],
        field_type=Types.array,
        items_type=Types.string,
        items_format=Formats.tag,
    )
    array_string_version: OperatorTypeMap = OperatorTypeMap(
        name="array_string_version",
        operators=[
            Operators.exists_array,
            *ops_clean(string_version.operators, [Operators.exists]),
        ],
        field_type=Types.array,
        field_format=Formats.version,
        items_type=Types.string,
        items_format=Formats.version,
    )
    array_string_datetime: OperatorTypeMap = OperatorTypeMap(
        name="array_string_datetime",
        operators=[
            Operators.exists_array,
            *ops_clean(string_datetime.operators, [Operators.exists]),
        ],
        field_type=Types.array,
        field_format=Formats.datetime,
        items_type=Types.string,
        items_format=Formats.datetime,
    )
    array_string_subnet: OperatorTypeMap = OperatorTypeMap(
        name="array_string_subnet",
        operators=[
            Operators.exists_array,
            *ops_clean(string_subnet.operators, [Operators.exists]),
        ],
        field_type=Types.array,
        field_format=Formats.subnet,
        items_type=Types.string,
        items_format=Formats.subnet,
    )
    array_discrete_string_logo: OperatorTypeMap = OperatorTypeMap(
        name="array_discrete_string_logo",
        operators=[
            Operators.exists_array,
            Operators.equals_str_adapter,
            Operators.count_equals,
            Operators.count_less_than,
            Operators.count_more_than,
            Operators.is_in_str_adapter,
        ],
        field_type=Types.array,
        field_format=Formats.discrete,
        items_type=Types.string,
        items_format=Formats.logo,
    )
    array_string_ip: OperatorTypeMap = OperatorTypeMap(
        name="array_string_ip",
        operators=[
            Operators.exists_array,
            *ops_clean(string_ip.operators, [Operators.exists]),
        ],
        field_type=Types.array,
        field_format=Formats.ip,
        items_type=Types.string,
        items_format=Formats.ip,
    )

    @classmethod
    def get_type_map(cls, field: dict) -> OperatorTypeMap:
        """Get the type mapping for a field."""

        def attrs_str(attrs):
            return ", ".join([f"{k}: {v!r}" for k, v in attrs.items()])

        def enum_val(obj, attr):
            value = getattr(obj, attr, None)
            return value.value if value else value

        items = field.get("items") or {}

        attrs = {
            "field_type": field["type"],
            "field_format": field.get("format"),
            "items_type": items.get("type"),
            "items_format": items.get("format"),
        }

        valid = {}

        typemaps = cls.get_fields()
        for typemap in typemaps:
            type_attrs = {k: enum_val(typemap.default, k) for k in attrs}
            valid[typemap.name] = type_attrs
            if type_attrs == attrs:
                typemap.default.name = typemap.name
                return typemap.default

        name = field["name_qual"]
        err = f"Unable to map field {name!r} with {attrs_str(attrs)}"
        valid_str = "\n  ".join([f"{k}: {attrs_str(v)}" for k, v in valid.items()])
        raise NotFoundError("\n".join([err, valid_str, err]))

    @classmethod
    def get_operator(cls, field: dict, operator: str):
        operator = operator.lower().strip()
        type_map = cls.get_type_map(field=field)
        for op in type_map.operators:
            if operator == op.name.name:
                return op

        name = field["name"]
        if field["parent"] != "root":
            parent = field["parent"]
            name = f"{name} (sub field of {parent})"

        valid = "\n - " + "\n - ".join([x.name.name for x in type_map.operators])
        raise NotFoundError(
            f"Invalid operator {operator!r} for field {name!r}, valids:{valid}"
        )

    @classmethod
    def get_map(cls) -> dict:
        op_map = {}

        typemaps = cls.get_fields()
        for typemap in typemaps:
            type_name = typemap.name
            for op in typemap.default.operators:
                op_name = op.name.name
                if op_name not in op_map:
                    op_map[op_name] = []
                op_map[op_name].append(type_name)
        return op_map


CUSTOM_FIELDS_MAP: Dict[str, List[dict]] = {
    "agg": [
        {
            "adapter_name_raw": f"{AGG_ADAPTER_NAME}_adapter",
            "adapter_name": AGG_ADAPTER_NAME,
            "adapter_title": AGG_ADAPTER_TITLE,
            "adapter_prefix": "specific_data",
            "column_name": f"{AGG_ADAPTER_NAME}:connection_label",
            "column_title": f"{AGG_ADAPTER_TITLE}: Adapter Connection Label",
            "sub_fields": [],
            "is_complex": False,
            "is_list": True,
            "is_root": True,
            "parent": "root",
            "name": "specific_data.connection_label",
            "name_base": "connection_label",
            "name_qual": "specific_data.connection_label",
            "title": "Adapter Connection Label",
            "type": "string",
            "format": "connection_label",
            "type_norm": "string_cnx_label",
            "is_agg": True,
            "expr_field_type": AGG_EXPR_FIELD_TYPE,
        },
    ]
}
