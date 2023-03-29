# -*- coding: utf-8 -*-
"""Utilities used by tools.

"Utilities are not just services, they are necessities."
"""
import typing as t
import types


def safe_cls_str(value: t.Any, include_module: bool = True) -> str:
    """Get the name and module of a class type.

    Args:
        value (t.Any):
            Value to get string with name and module.
        include_module (bool):
            Prefix the type name with the type module.

    Returns:
        str:
            The name and module of value as "module.name".
    """
    if value is None:
        name: str = "None"
        module: str = ""
    else:
        fallback: t.Optional[type] = getattr(value, "__class__", None)
        name: str = safe_getattr(attr="__name__", value=value, fallback=fallback, final="")
        module: str = safe_getattr(attr="__module__", value=value, fallback=fallback, final="")
        if module == "builtins":
            module = ""

    return ".".join([x for x in [module if include_module else "", name] if x])


def safe_len_str(value: t.Any, prefix: str = "", only_types: t.Any = None) -> str:
    """Get a string that describes the length of value.

    Args:
        value (t.Any):
            If value is one of only_types, return prefix + length of value.
        prefix:
            prefix to add to the length of value.
        only_types:
            If value is not one of these types, return an empty string.

    Returns:
        str:
            The length of value or an empty string.
    """
    if only_types is not None and not safe_is_instance(value=value, expected_types=only_types):
        return ""

    return f"{prefix}{safe_len(value)}"


def safe_getattr(
    attr: str, value: t.Any = None, fallback: t.Any = None, final: t.Any = None
) -> t.Any:
    """Get the value of an attribute from value, fallback, or final.

    Args:
        attr:
            Attribute to try to get from value, or fallback.
        value:
            Value to try to get attribute from first.
        fallback:
            Value to try to get attribute from second.
        final:
           Value to return if value nor fallback have the attribute.

    Returns:
        t.Any:
            Value of attr from value, fallback, or final.
    """
    # noinspection PyBroadException
    try:
        return getattr(value, attr, getattr(fallback, attr, final))
    except Exception:
        return final


def safe_len(value: t.Any) -> int:
    """Try to get the length of value as an int.

    Args:
        value (t.Any):
            Value to get length of

    Returns:
        int:
            The length of value or 0.
    """
    # noinspection PyBroadException
    try:
        return len(value)
    except Exception:
        return 0


def safe_get_origin(value: t.Any) -> t.Any:
    """Get the origin of a typing type.

    Args:
        value (t.Any):
            Value to get origin of.

    Returns:
        t.Any:
            The origin of value.
    """
    # noinspection PyBroadException
    try:
        return t.get_origin(value)
    except Exception:
        return None


def safe_get_type_hints(value: t.Any) -> dict:
    """Get the type hints for value.

    Args:
        value (t.Any):
            Value to get type hints for.

    Returns:
        dict:
            Type hints for value.
    """
    # noinspection PyBroadException
    try:
        return t.get_type_hints(value)
    except Exception:
        return {}


def safe_is_type(
    value: t.Any,
    expected_types: t.Any = None,
    any_types: t.Optional[t.Union[t.List[t.Any], t.Tuple[t.Any]]] = (t.Any, None),
) -> bool:
    """Determine if value is an instance of the type for this field."""
    return (
        (expected_types is None)
        or (any_types and expected_types in any_types)
        or (safe_is_instance(value=value, expected_types=expected_types))
    )


def safe_is_instance(value: t.Any, expected_types: t.Any = None) -> bool:
    """Determine if value is an instance of the type for this field."""
    try:
        return isinstance(value, expected_types)
    except TypeError:
        return False


def safe_is_subclass(value: t.Any, expected_types: t.Any = None) -> bool:
    """Determine if value is a subclass of the type for this field."""
    try:
        return issubclass(value, expected_types)
    except TypeError:
        return False


def is_class_var(value: t.Any) -> bool:
    """Check if value is a typing.ClassVar."""
    # noinspection PyBroadException
    return safe_get_origin(value=value) == t.ClassVar or "ClassVar" in str(value)


def get_type_hints(value: t.Any, include_class_vars: bool = False) -> t.Dict[str, type]:
    """Get the type hints for value.

    Args:
        include_class_vars:
            Include type hints that are ClassVars.
        value (t.Any):
            Value to get type hints for.

    Returns:
        dict:
            Type hints for value.
    """
    # noinspection PyBroadException
    hints = safe_get_type_hints(value=value)
    if not include_class_vars:
        hints = {k: v for k, v in hints.items() if not is_class_var(v)}
    return hints


def listify(
    value: t.Any = None, callbacks: t.Optional[t.Dict[t.Any, callable]] = None, **kwargs
) -> t.Union[t.List[t.Any], types.GeneratorType]:
    """Coerce a value to a list.

    Notes:
        If value is None, return an empty list.
        If value is a generator, return the generator.
        If value is a list, return the list.
        If value is a tuple or set, return a list of value.
        If value is not None, return a list with value as the only item.

    Args:
        value:
            object to coerce to list
        callbacks:
            dict of types and callbacks to call if value is an instance of the type
    """
    if isinstance(callbacks, dict):
        for expected_types, callback in callbacks.items():
            if safe_is_instance(value, expected_types) and callable(callback):
                value: t.Any = callback(value=value, **kwargs)
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, types.GeneratorType):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    return [value]
