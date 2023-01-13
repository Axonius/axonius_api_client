# -*- coding: utf-8 -*-
"""Custom types."""
import pathlib
import typing as t

PathLike: t.TypeVar = t.TypeVar("PathLike", pathlib.Path, str, bytes)
PatternLike: t.TypeVar = t.TypeVar("PatternLike", t.Pattern, str, bytes)
PatternLikeListy: t.TypeVar = t.TypeVar("PatternLikeListy", PatternLike, t.List[PatternLike])
ComplexLike: t.Tuple[t.Type] = (dict, list, tuple)
SimpleLike: t.Tuple[t.Type] = (str, int, bool, float)


# STR_RE = t.Union[str, t.Pattern]
# STR_RE_LISTY = t.Union[STR_RE, t.List[STR_RE]]
# OPT_STR_RE_LISTY = t.Optional[STR_RE_LISTY]
