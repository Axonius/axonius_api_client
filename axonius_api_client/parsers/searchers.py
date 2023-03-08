# -*- coding: utf-8 -*-
"""Fancy footwork for searching objects based on attributes."""
import collections
import dataclasses
import re
import typing as t

from ..constants.api import FolderDefaults
from ..tools import is_pattern, is_str, listify


class Counter(collections.Counter):
    """Add a human string to counter mapping."""

    def get_strs(self) -> t.List[str]:
        """Pass."""
        return [f"{v} {k} objects" for k, v in self.items()] or ["0 objects"]

    def __str__(self):
        """Pass."""
        return " and ".join(self.get_strs())

    def __repr__(self):
        """Pass."""
        return self.__str__()


@dataclasses.dataclass(repr=False)
class Search:
    """Container for a search value provided by a user."""

    value: t.Any = None
    pattern_prefix: t.Optional[str] = FolderDefaults.pattern_prefix
    ignore_case: bool = FolderDefaults.ignore_case

    equals: t.ClassVar[t.Optional[str]] = None
    pattern: t.ClassVar[t.Optional[t.Pattern]] = None
    matched: t.ClassVar[bool] = False

    def __post_init__(self):
        """Pass."""
        if is_str(self.value):
            if is_str(self.pattern_prefix) and self.value.lstrip().startswith(self.pattern_prefix):
                flags: int = re.I if self.ignore_case else 0
                prefix_length: int = len(self.pattern_prefix)
                value: str = self.value.lstrip()[prefix_length:]
                self.pattern: t.Pattern = re.compile(value, flags=flags)
            else:
                self.equals: str = self.value
        if is_pattern(self.value):
            self.pattern: t.Pattern = self.value

    def is_attr_value_match(self, obj: t.Any) -> bool:
        """Pass."""
        return self.is_value_match(value=getattr(obj, self.attr, None))

    def is_value_match(self, value: t.Any) -> bool:
        """Pass."""
        if (self.equals is not None and self.equals == value) or (
            self.pattern is not None and self.pattern.search(value)
        ):
            self.matched = True
            return True
        return False

    @property
    def attr(self) -> str:
        """Pass."""
        return "name"

    @property
    def search(self) -> t.Optional[t.Union[str, t.Pattern]]:
        """Pass."""
        return self.pattern if self.pattern is not None else self.equals

    def __str__(self):
        """Pass."""
        items: t.List[str] = [
            f"attr={self.attr!r}",
            f"search={self.search!r}",
            f"matched={self.matched!r}",
        ]
        items: str = ", ".join(items)
        return f"{self.__class__.__name__}({items})"

    def __repr__(self):
        """Pass."""
        return self.__str__()


@dataclasses.dataclass(repr=False)
class Searches:
    """Pass."""

    objects: t.List[object]
    values: t.Optional[t.List[str]] = None
    pattern_prefix: t.Optional[str] = FolderDefaults.pattern_prefix
    ignore_case: bool = FolderDefaults.ignore_case

    searches: t.ClassVar[t.List[Search]] = None
    matches: t.ClassVar[t.List[object]] = None

    def __post_init__(self):
        """Pass."""
        self.objects: t.List[object] = listify(self.objects)
        self.matches: t.List[object] = []
        self.searches: t.List[Search] = [
            Search(value=x, ignore_case=self.ignore_case, pattern_prefix=self.pattern_prefix)
            for x in listify(self.values)
        ]

        for obj in self.objects:
            for search in self.searches:
                matched: bool = search.is_attr_value_match(obj=obj)
                if matched and obj not in self.matches:
                    self.matches.append(obj)

    @property
    def objects_cls_names(self) -> t.List[str]:
        """Pass."""
        return [y for y in [self._get_cls_name(x) for x in self.objects] if is_str(y)]

    @property
    def count_objects(self) -> Counter:
        """Pass."""
        return Counter(self.objects_cls_names)

    @property
    def count_searches(self) -> int:
        """Pass."""
        return len(self.searches)

    @property
    def count_unmatched(self) -> int:
        """Pass."""
        return len(self.unmatched)

    @property
    def count_matches(self) -> int:
        """Pass."""
        return len(self.matches)

    @property
    def unmatched(self) -> t.List[Search]:
        """Pass."""
        return [x for x in self.searches if x.matched is not True]

    @property
    def str_matches(self) -> str:
        """Pass."""
        return (
            f"Found {self.count_matches} matches from {self.count_searches} searches "
            f"against {self.count_objects}"
        )

    @property
    def str_unmatched(self) -> str:
        """Pass."""
        return (
            f"{self.count_unmatched} of {self.count_searches} searches did not match "
            f"against {self.count_objects}"
        )

    @staticmethod
    def _get_cls_name(value: t.Any) -> t.Optional[str]:
        """Pass."""
        if hasattr(value, "__class__"):
            value = value.__class__
        if hasattr(value, "__name__"):
            value = value.__name__
        return value if is_str(value) else None

    def __str__(self):
        """Pass."""
        attrs: t.List[str] = [
            f"searches={self.count_searches!r}",
            f"objects={self.count_objects}",
            f"matches={self.count_matches!r}",
            f"unmatched={self.count_unmatched!r}",
            f"ignore_case={self.ignore_case!r}",
            f"pattern_prefix={self.pattern_prefix!r}",
        ]
        searches: t.List[str] = (
            [f" - {x}" for x in self.searches] if self.searches else [" - No searches supplied!"]
        )
        items: t.List[str] = [
            f"{self.__class__.__name__}({', '.join(attrs)}):",
            *searches,
        ]
        ret: str = "\n".join(items)
        return ret

    def __repr__(self):
        """Pass."""
        return self.__str__()
