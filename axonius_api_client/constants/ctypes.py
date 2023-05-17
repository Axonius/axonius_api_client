"""Custom types."""
import datetime
import pathlib
import typing as t

PathLike = t.TypeVar("PathLike", pathlib.Path, str, bytes)
PatternLike = t.TypeVar("PatternLike", t.Pattern, str, bytes)
PatternLikeListy = t.Union[PatternLike, t.Iterable[PatternLike]]
ComplexLike: t.Tuple[t.Type, ...] = (dict, list, tuple)
SimpleLike: t.Tuple[t.Type, ...] = (str, int, bool, float)
Refreshables = t.Optional[t.Union[str, bytes, int, float, bool]]
TypeDate = t.TypeVar("TypeDate", str, bytes, datetime.datetime, datetime.timedelta)
TypeDelta = t.TypeVar("TypeDelta", str, bytes, float, int, datetime.timedelta)
TypeFloat = t.TypeVar("TypeFloat", float, int, str, bytes)
TypeMatch = t.TypeVar(
    "TypeMatch",
    str,
    bytes,
    t.Pattern,
    t.List[t.Union[str, bytes, t.Pattern]],
    t.Tuple[t.Union[str, bytes, t.Pattern]],
)
TypeInt = t.TypeVar("TypeInt", int, str, bytes)
TypeBool = t.TypeVar("TypeBool", bool, str, bytes, int, float)


class FolderBase:
    """baseclass for all folder types."""
