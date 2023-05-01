# -*- coding: utf-8 -*-
"""Parsers for field schemas."""
import copy
from typing import List, Optional

from ..constants.fields import (
    AGG_ADAPTER_NAME,
    AGG_ADAPTER_TITLE,
    AGG_EXPR_FIELD_TYPE,
    ALL_NAME,
    RAW_NAME,
    OperatorTypeMaps,
)
from ..tools import strip_left, strip_right


def parse_fields(raw: dict) -> dict:
    """Parse all generic and adapter specific fields.

    Args:
        raw: field schemas returned by :meth:`axonius_api_client.api.assets.fields.Fields._get`
    """
    agg_fields: List[dict] = parse_schemas(
        adapter_name=AGG_ADAPTER_NAME,
        adapter_title=AGG_ADAPTER_TITLE,
        adapter_name_raw=f"{AGG_ADAPTER_NAME}_adapter",
        adapter_prefix="specific_data.data",
        all_field="specific_data",
        raw_fields=raw["generic"],
    )

    agg_base_names: List[str] = [x["name_base"] for x in agg_fields]

    parsed = {}
    parsed[AGG_ADAPTER_NAME] = agg_fields

    for raw_name, raw_fields in raw["specific"].items():
        # raw_name = aws_adapter

        prefix = f"adapters_data.{raw_name}"
        # prefix = adapters_data.aws_adapter

        name = strip_right(obj=raw_name, fix="_adapter")
        # name = aws

        title = " ".join(name.split("_")).title()

        fields = parse_schemas(
            adapter_name_raw=raw_name,
            adapter_name=name,
            adapter_prefix=prefix,
            adapter_title=title,
            all_field=prefix,
            raw_fields=raw_fields,
            agg_base_names=agg_base_names,
        )

        parsed[name] = fields

    return parsed


def is_complex(field: dict) -> bool:
    """Determine if a field is complex from its schema.

    Args:
        field: field schema to parse
    """
    field_type = field["type"]
    field_items = field.get("items", {})

    if isinstance(field_items, dict):  # pragma: no cover
        field_items_type = field_items.get("type")
        if field_type == "array" and field_items_type == "array":
            return True

    return False


def is_root(name: str, names: List[str]) -> bool:
    """Determine if a field is a root field.

    Args:
        name: name of current field
        names: names of all fields
    """
    dots = name.split(".")
    return not (len(dots) > 1 and dots[0] in names)


def parse_complex(field: dict):
    """Parse a complex field schema.

    Args:
        field: complex field schema
    """
    field["is_complex"] = is_complex(field=field)
    if field["is_complex"]:
        col_title = field["column_title"]
        col_name = field["column_name"]
        name_base = field["name_base"]
        prefix = field["adapter_prefix"]
        items = field["items"].pop("items")
        adapter_name = field["adapter_name"]
        adapter_name_raw = field["adapter_name_raw"]
        adapter_prefix = field["adapter_prefix"]
        adapter_title = field["adapter_title"]
        parent = field["name_qual"]
        expr_field_type = field["expr_field_type"]
        is_agg = field["is_agg"]

        field["sub_fields"] = sub_fields = []
        field_names = [f["name"] for f in items]

        for sub_field in items:
            sub_title = sub_field["title"]
            sub_name = sub_field["name"]
            sub_name_base = f"{name_base}.{sub_name}"
            sub_name_qual = f"{prefix}.{sub_name_base}"

            sub_field["name_base"] = sub_name_base
            sub_field["name_qual"] = sub_name_qual
            sub_field["is_root"] = is_root(name=sub_name, names=field_names)
            sub_field["is_list"] = sub_field["type"] == "array"
            sub_field["parent"] = parent
            sub_field["adapter_name"] = adapter_name
            sub_field["adapter_name_raw"] = adapter_name_raw
            sub_field["adapter_prefix"] = adapter_prefix
            sub_field["adapter_title"] = adapter_title
            sub_field["column_title"] = f"{col_title}: {sub_title}"
            sub_field["column_name"] = f"{col_name}.{sub_name}"
            sub_field["is_agg"] = is_agg
            sub_field["expr_field_type"] = expr_field_type
            sub_field["is_details"] = field["is_details"]
            sub_field["is_all"] = False
            type_map = OperatorTypeMaps.get_type_map(field=sub_field)
            sub_field["type_norm"] = type_map.name
            sub_field["selectable"] = True
            parse_complex(field=sub_field)
            sub_fields.append(sub_field)


def parse_schemas(
    adapter_name_raw: str,
    adapter_name: str,
    adapter_prefix: str,
    adapter_title: str,
    all_field: str,
    raw_fields: List[dict],
    agg_base_names: Optional[List[str]] = None,
) -> List[dict]:
    """Parse field schemas for an adapter.

    Args:
        adapter_name_raw: raw name of current adapter (aws_adapter)
        adapter_name: user-friendly name of current adapter (aws)
        adapter_prefix: fully qualified prefix of adapter (specific_data.data or
            adapters_data.aws_adapter)
        adapter_title: user-friendly title of adapter
        all_field: name to use for all field schema
        raw_fields: raw unparsed fields for current adapter
        agg_base_names: used to determine if a field is aggregated or not
    """
    agg_base_names = agg_base_names or []
    is_agg = adapter_name == AGG_ADAPTER_NAME

    fields = [
        {
            "adapter_name_raw": adapter_name_raw,
            "adapter_name": adapter_name,
            "adapter_title": adapter_title,
            "adapter_prefix": adapter_prefix,
            "column_name": f"{adapter_name}:{ALL_NAME}",
            "column_title": f"All {adapter_title} Data",
            "sub_fields": [],
            "is_complex": True,
            "is_list": True,
            "is_root": False,
            "parent": "root",
            "name": ALL_NAME,
            "name_base": ALL_NAME,
            "name_qual": all_field,
            "title": "All Adapter Specific Data",
            "type": "array",
            "type_norm": "array_object_object",
            "selectable": True,
            "is_agg": is_agg,
            "expr_field_type": AGG_EXPR_FIELD_TYPE,
            "is_details": False,
            "is_all": True,
        },
        {
            "adapter_name_raw": adapter_name_raw,
            "adapter_name": adapter_name,
            "adapter_title": adapter_title,
            "adapter_prefix": adapter_prefix,
            "column_name": f"{adapter_name}:{RAW_NAME}",
            "column_title": f"{adapter_title} Raw Data",
            "sub_fields": [],
            "is_complex": True,
            "is_list": True,
            "is_root": False,
            "parent": "root",
            "name": f"{adapter_prefix}.{RAW_NAME}",
            "name_base": RAW_NAME,
            "name_qual": f"{adapter_prefix}.{RAW_NAME}",
            "title": "Adapter Raw Data",
            "type": "array",
            "type_norm": "array_object_object",
            "selectable": True,
            "is_agg": is_agg,
            "expr_field_type": AGG_EXPR_FIELD_TYPE,
            "is_details": False,
            "is_all": False,
        },
    ]
    if is_agg:
        fields += [
            {
                "adapter_name_raw": adapter_name_raw,
                "adapter_name": adapter_name,
                "adapter_title": adapter_title,
                "adapter_prefix": adapter_prefix,
                "column_name": f"{adapter_name}:unique_adapter_names_details",
                "column_title": "Unique Adapter Names Details Index",
                "sub_fields": [],
                "is_complex": False,
                "is_list": True,
                "is_root": True,
                "parent": "root",
                "name": "unique_adapter_names_details",
                "name_base": "unique_adapter_names_details",
                "name_qual": "unique_adapter_names_details",
                "title": "Unique Adapter Names Details Index",
                "type": "array",
                "type_norm": "array_string",
                "selectable": False,
                "is_agg": is_agg,
                "expr_field_type": AGG_EXPR_FIELD_TYPE,
                "is_details": True,
                "is_all": False,
            },
            {
                "adapter_name_raw": adapter_name_raw,
                "adapter_name": adapter_name,
                "adapter_title": adapter_title,
                "adapter_prefix": adapter_prefix,
                "column_name": f"{adapter_name}:meta_data.client_used",
                "column_title": "Adapter Connection Details Index",
                "sub_fields": [],
                "is_complex": False,
                "is_list": True,
                "is_root": True,
                "parent": "root",
                "name": "meta_data.client_used",
                "name_base": "meta_data.client_used",
                "name_qual": "meta_data.client_used",
                "title": "Adapter Connection Details Index",
                "type": "array",
                "type_norm": "array_string",
                "selectable": False,
                "is_agg": is_agg,
                "expr_field_type": AGG_EXPR_FIELD_TYPE,
                "is_details": True,
                "is_all": False,
            },
            {
                "adapter_name_raw": adapter_name_raw,
                "adapter_name": adapter_name,
                "adapter_title": adapter_title,
                "adapter_prefix": adapter_prefix,
                "column_name": f"{adapter_name}:adapter_asset_entities_info",
                "column_title": "Adapter Asset Entity Info",
                "sub_fields": [],
                "is_complex": False,
                "is_list": True,
                "is_root": True,
                "parent": "root",
                "name": "adapter_asset_entities_info",
                "name_base": "adapter_asset_entities_info",
                "name_qual": "adapter_asset_entities_info",
                "title": "Adapter Asset Entity Info",
                "type": "array",
                "type_norm": "array_string",
                "selectable": False,
                "is_agg": is_agg,
                "expr_field_type": AGG_EXPR_FIELD_TYPE,
                "is_details": True,
                "is_all": False,
            },
        ]

    field_names = [strip_left(obj=f["name"], fix=adapter_prefix).strip(".") for f in raw_fields]

    for field in raw_fields:
        title = field["title"]
        name_base = strip_left(obj=field["name"], fix=adapter_prefix).strip(".")
        field["adapter_name"] = adapter_name
        field["adapter_title"] = adapter_title
        field["adapter_prefix"] = adapter_prefix
        field["adapter_name_raw"] = adapter_name_raw
        field["name_base"] = name_base
        field["name_qual"] = field["name"]
        field["is_root"] = is_root(name=name_base, names=field_names)
        field["is_list"] = field["type"] == "array"
        field["parent"] = "root"
        field["column_title"] = f"{adapter_title}: {title}"
        field["column_name"] = f"{adapter_name}:{name_base}"
        type_map = OperatorTypeMaps.get_type_map(field=field)
        field["type_norm"] = type_map.name
        field["selectable"] = True
        field["is_agg"] = bool(agg_base_names) and name_base in agg_base_names
        field["is_details"] = False
        field["is_all"] = False
        if adapter_name == AGG_ADAPTER_NAME:
            field["expr_field_type"] = AGG_EXPR_FIELD_TYPE
        else:
            field["expr_field_type"] = adapter_name_raw

        parse_complex(field=field)
        fields.append(field)

        field_details = copy.deepcopy(field)
        field_details["name"] += "_details"
        field_details["name_base"] += "_details"
        field_details["name_qual"] += "_details"
        field_details["column_title"] += " Details"
        field_details["column_name"] += "_details"
        field_details["selectable"] = False
        field_details["is_details"] = True
        fields.append(field_details)

    return fields


def schema_custom(name: str, **kwargs) -> dict:
    """Create a custom field schema."""
    unknown = kwargs.get("unknown", "custom")
    adapter_name = kwargs.get("adapter_name", unknown)
    adapter_name_raw = kwargs.get("adapter_name_raw", unknown)
    adapter_title = kwargs.get("adapter_title", unknown.capitalize())
    adapter_prefix = kwargs.get("adapter_name_raw", unknown[:2])
    title = name.capitalize()
    column_name = kwargs.get("column_name", f"{adapter_name}:{name}")
    column_title = kwargs.get("column_title", f"{adapter_title}: {title}")
    ftype = kwargs.get("type", "string")
    ftype_norm = kwargs.get("type_name", "string")
    return {
        "adapter_name_raw": adapter_name_raw,
        "adapter_name": adapter_name,
        "adapter_title": adapter_title,
        "adapter_prefix": adapter_prefix,
        "column_name": column_name,
        "column_title": column_title,
        "sub_fields": [],
        "is_complex": False,
        "is_list": False,
        "is_root": True,
        "parent": "root",
        "name": name,
        "name_base": name,
        "name_qual": name,
        "title": title,
        "type": ftype,
        "type_norm": ftype_norm,
        "selectable": False,
        "is_agg": False,
        "expr_field_type": "agg",
        "is_details": False,
        "is_all": False,
    }
