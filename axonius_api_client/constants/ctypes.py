# -*- coding: utf-8 -*-
"""Custom types."""
import datetime
import pathlib
import typing as t

PathLike: t.TypeVar = t.TypeVar("PathLike", pathlib.Path, str, bytes)
PatternLike: t.TypeVar = t.TypeVar("PatternLike", t.Pattern, str, bytes)
PatternLikeListy: t.Type = t.Union[PatternLike, t.Iterable[PatternLike]]
ComplexLike: t.Tuple[t.Type, ...] = (dict, list, tuple)
SimpleLike: t.Tuple[t.Type, ...] = (str, int, bool, float)
Refreshables: t.Type = t.Optional[t.Union[str, bytes, int, float, bool]]
TypeDate: t.TypeVar = t.TypeVar("TypeDate", str, bytes, datetime.datetime, datetime.timedelta)
TypeDelta: t.TypeVar = t.TypeVar("TypeDelta", str, bytes, float, int, datetime.timedelta)
TypeFloat: t.TypeVar = t.TypeVar("TypeFloat", float, int, str, bytes)
TypeMatch: t.TypeVar = t.TypeVar(
    "TypeMatch",
    str,
    bytes,
    t.Pattern,
    t.List[t.Union[str, bytes, t.Pattern]],
    t.Tuple[t.Union[str, bytes, t.Pattern]],
)
TypeInt: t.TypeVar = t.TypeVar("TypeInt", int, str, bytes)
TypeBool: t.TypeVar = t.TypeVar("TypeBool", bool, str, bytes, int, float)


class FolderBase:
    """baseclass for all folder types."""


# STR_RE = t.Union[str, t.Pattern]
# STR_RE_LISTY = t.Union[STR_RE, t.List[STR_RE]]
# OPT_STR_RE_LISTY = t.Optional[STR_RE_LISTY]
