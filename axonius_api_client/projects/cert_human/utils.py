# -*- coding: utf-8 -*-
"""Tools for working with SSL certificate files."""
import base64
import logging
from typing import Any, List, Optional, Type, Union

LOG: logging.Logger = logging.getLogger(__name__)
HUMAN_KEY_ALIGN: int = 32
HUMAN_CAP_WORDS: List[str] = ["id", "url", "crl", "sha256", "sha1", "ssl"]


def parse_url(url: str) -> str:
    """Pass."""
    try:
        from url_parser import UrlParser

        url_parsed = UrlParser(url=url, default_scheme="https")
        return url_parsed.url
    except ImportError:
        return url


def type_str(value: Any, max_len: int = 60, join: Optional[str] = ", ") -> Union[str, List[str]]:
    """Pass."""
    length = len(str(value))
    svalue = f"{str(value)[:max_len]}...snip..." if length >= max_len else f"{value}"
    items = [
        f"type={type(value)}",
        f"length={length}",
        f"value={svalue!r}",
    ]
    return join.join(items) if isinstance(join, str) else items


def human_key_align(key: str, indent: int = 2) -> str:
    """Pass."""
    space = " " * indent
    pre = f"{space}- {{k}}".format
    return f"{pre(k=human_key(key)):<{HUMAN_KEY_ALIGN}}"


def human_key_value(key: str, value: str, indent: int = 2) -> str:
    """Pass."""
    return f"{human_key_align(key=key, indent=indent)}: {value}"


def human_key(value: str) -> str:
    """Pass."""

    def word(w):
        if w.isupper():
            return w
        if w.lower() in HUMAN_CAP_WORDS:
            return w.upper()
        return w.title()

    check_type(value=value, exp=str)
    value = value.replace("_", " ").strip()
    value = " ".join([word(x) for x in value.split()])
    return value


def human_dict(value: dict, indent: int = 2) -> List[str]:
    """Pass."""

    def handle(k, v):
        if isinstance(v, list) and all([isinstance(x, dict) for x in v]):
            for idx, sub_v in enumerate(v):
                kn = f"{k} item #{idx + 1}:"
                yield f"{human_key_align(key=kn, indent=indent)}"
                yield from human_dict(value=sub_v, indent=indent + 2)
        else:
            yield human_key_value(key=k, value=v, indent=indent)

    check_type(value=value, exp=dict)
    items = []
    for k, v in value.items():
        items += list(handle(k, v))
    return items


def check_type(value: Any, exp: Type[Any], allow_none: bool = False):
    """Pass."""
    if value is None and not allow_none:
        raise TypeError(f"Value is required and must be {exp}, not None")

    if not isinstance(value, exp):
        raise TypeError(f"Value must be type {exp}, not {type_str(value)}")


def get_subcls(cls: type, excludes: Optional[List[type]] = None) -> list:
    """Get all subclasses of a class."""
    excludes = excludes or []
    subs = [s for c in cls.__subclasses__() for s in get_subcls(c)]
    return [x for x in list(set(cls.__subclasses__()).union(subs)) if x not in excludes]


def bytes_to_b64(value: Union[str, bytes], strict: bool = True, encoding: str = "utf-8") -> str:
    """Pass."""
    check_type(value=value, exp=(str, bytes))
    value = str_to_bytes(value=value, strict=strict, encoding=encoding)
    return bytes_to_str(value=base64.b64encode(value))


def bytes_to_str(value: Union[str, bytes], strict: bool = True, encoding: str = "utf-8") -> bytes:
    """Coerce bytes into str."""
    check_type(value=value, exp=(str, bytes))
    errors = "strict" if strict else "replace"
    return value.decode(encoding, errors) if isinstance(value, bytes) else value


def bytes_to_hex(value: bytes) -> str:
    """Pass."""
    check_type(value=value, exp=bytes)
    return ":".join(f"{x:02X}" for x in value)


def b64_to_hex(value: Union[str, bytes], strict: bool = True) -> str:
    """Pass."""
    return bytes_to_hex(value=b64_to_bytes(value=value, strict=strict))


def b64_to_bytes(value: Union[str, bytes], strict: bool = True, encoding: str = "utf-8") -> bytes:
    """Pass."""
    check_type(value=value, exp=(str, bytes))
    return base64.b64decode(str_to_bytes(value=value, strict=strict, encoding=encoding))


def int_to_hex(value: int) -> str:
    """Pass."""
    check_type(value=value, exp=int)
    value = f"{value:X}".upper()
    return ":".join([value[i : i + 2] for i in range(0, len(value), 2)])  # noqa: E203


def str_to_bytes(value: Union[str, bytes], strict: bool = True, encoding: str = "utf-8") -> bytes:
    """Coerce string into bytes."""
    check_type(value=value, exp=(str, bytes))
    errors = "strict" if strict else "replace"
    return value.encode(encoding, errors) if isinstance(value, str) else value


def str_strip_to_int(value: str) -> Optional[int]:
    """Pass."""
    check_type(value=value, exp=str)
    digit = "".join([x for x in value if x.isdigit()])
    return int(digit) if digit.isdigit() else None


def listify(value: Any, dictkeys: bool = False) -> list:
    """Force an object into a list."""
    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if value is None:
        return []

    if isinstance(value, dict) and dictkeys:
        return list(value)

    return [value]
