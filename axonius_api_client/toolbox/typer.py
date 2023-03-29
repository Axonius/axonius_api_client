# -*- coding: utf-8 -*-
"""Tool for getting type-related information about Python objects.

"I have not failed. I've just found 10,000 ways that won't work."
 - Thomas A. Edison
"""
import collections
import typing as t

from .tool import Tool, Fields, fields_generate, fields_parse


@fields_generate
class Typer(Tool):
    """Tool for getting type-related information about Python objects."""

    include_module: bool = False
    """Prefix the type name with the type module."""
    include_length: bool = True
    """Append the length of value in to the type name."""
    include_count: bool = True
    """Append iterator type counts in to the type name."""

    @classmethod
    @fields_parse()
    def _use(cls, value: t.Any, **kwargs) -> str:
        """Build a string that describes the type, module, and iterator counts.

        Args:
            value (t.Any):
                Value to get string with type, module, and iterator counts.
            **kwargs:
                include_module (bool): Prefix the type name with the type module.
                include_length (bool): Append the length of value in to the type name.
                include_count (bool): Append iterator type counts in to the type name.

        Returns:
            str:
                String with the type, module, and iterator counts of value.
        """
        fields: Fields = cls.get_fields(**kwargs)
        include_length: bool = fields.include_length.value
        include_count: bool = fields.include_count.value
        include_module: bool = fields.include_module.value

        name: str = cls.UTILITY.safe_cls_str(value=value, include_module=include_module)
        if include_length and isinstance(value, (str, bytes, list, tuple, set, dict)):
            length = cls.UTILITY.safe_len_str(value=value, prefix="length=")
            if length:
                name = f"{name}({length})"

        if include_count and isinstance(value, (list, tuple, set, dict)):
            count_map: t.Dict[str, int] = collections.defaultdict(lambda: 0)
            items: t.Iterable[t.Any] = value.values() if isinstance(value, dict) else value
            for item in items:
                item_type: str = cls.use(value=item, fields=fields)
                count_map[item_type] += 1
            if count_map:
                counts: str = ", ".join([f"{k}={v}" for k, v in count_map.items()])
                name = f"{name}[{counts}]"

        return name
