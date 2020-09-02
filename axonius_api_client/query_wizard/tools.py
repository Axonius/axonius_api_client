# -*- coding: utf-8 -*-
"""Utilities for this package."""
from typing import List, Optional

from ..data_classes.wizard import ExprKeys
from ..exceptions import ToolsError
from ..tools import coerce_bool


def get_expr_lines(expr: dict, indent=0) -> str:
    itxt = " " * indent
    expr_lines = []

    for k, v in expr.items():
        if k.startswith("_"):
            continue

        if k == ExprKeys.SUBS:
            expr_lines.append(f"{itxt}- {k}:")
            for idx, sub in enumerate(v):
                lines = [
                    "",
                    f"Sub Expression #{idx + 1}",
                    get_expr_lines(expr=sub, indent=indent + 2),
                ]
                expr_lines += lines
        elif isinstance(v, dict):
            expr_lines.append(f"{itxt}- {k}:")
            expr_lines += [f"{itxt}  - {a}: {b!r}" for a, b in v.items()]
        else:
            expr_lines.append(f"{itxt}- {k}: {v!r}")

    expr_lines += []
    return "\n".join(expr_lines)


# XXX desc=?
def get_key_str(
    expr: dict, key: str, default="", valid: Optional[List[str]] = None
) -> str:
    value = expr.get(key, default)
    pre = f"Key {key}={value!r}"
    if not value or not isinstance(value, str):
        vtype = type(value).__name__
        raise ToolsError(f"{pre} must be a non-empty string, not {vtype}")
    value = value.strip().lower()
    if valid and value not in valid:
        valid = "\n - " + "\n - ".join(valid)
        raise ToolsError(f"{pre} it not a valid value, valids:{valid}")
    return value


def get_key_bool(expr: dict, key: str, default: bool = False) -> bool:
    value = expr.get(key, default)
    pre = f"Key {key}={value!r}"
    return coerce_bool(obj=value, errmsg=f"{pre} must be a boolean")


def get_key_lod(expr: dict, key: str) -> List[dict]:
    value = expr.get(key, []) or []
    pre = f"Key {key}={value!r}"
    if not value or not isinstance(value, (list, tuple)):
        vtype = type(expr).__name__
        raise ToolsError(f"{pre} must be a non-empty list of dictionaries, not {vtype}")
    for idx, item in enumerate(value):
        if not isinstance(item, dict):
            vtype = type(item).__name__
            raise ToolsError(
                f"{pre} item #{idx} must be a non-empty dictionary, not {vtype}"
            )
    return value
