# -*- coding: utf-8 -*-
"""Parsers for API models."""

import typing as t

import cachetools

from ..constants.api import RE_PREFIX
from ..constants.ctypes import PatternLike, PatternLikeListy
from ..constants.general import HIDDEN, SPLITTER
from ..tools import bytes_to_str, coerce_str_re, is_pattern, is_str, listify

CACHE_SIZE: int = 1024
MatcherLoad: t.TypeVar = t.TypeVar(
    "MatcherLoad", "Matcher", str, t.Pattern, t.Iterable[t.Union[str, t.Pattern]]
)


class Matcher:
    """Caching pattern matcher."""

    def _listify(self, value: t.Any) -> t.List[t.Any]:
        """Pass."""
        return listify(
            value=value,
            split=self.split,
            split_max=self.split_max,
            split_sep=self.split_sep,
            strip=self.strip,
            strip_chars=self.strip_chars,
        )

    def __init__(
        self,
        values: t.Optional[PatternLikeListy] = None,
        re_prefix: str = RE_PREFIX,
        split: bool = True,
        split_max: int = -1,
        split_sep: t.Optional[PatternLike] = SPLITTER,
        strip: bool = True,
        strip_chars: t.Optional[str] = None,
        hidden: t.Optional[str] = HIDDEN,
    ) -> None:
        """Pass."""
        self.values_orig: t.Optional[PatternLikeListy] = values
        self.re_prefix: str = re_prefix
        self.split: bool = split
        self.split_sep: t.Optional[PatternLike] = split_sep
        self.split_max: int = split_max
        self.strip: bool = strip
        self.strip_chars: t.Optional[str] = strip_chars
        self.hidden: t.Optional[str] = hidden
        self.strings: t.List[str] = []
        self.patterns: t.List[t.Pattern] = []
        self.values: t.List[t.Union[str, t.Pattern]] = self._listify(values)

        for value in self.values:
            for item in self._listify(value=value):
                check = coerce_str_re(value=item, prefix=self.re_prefix)
                if is_str(value=check, not_empty=True) and check not in self.strings:
                    self.strings.append(check)
                elif is_pattern(value=check) and check not in self.patterns:
                    self.patterns.append(check)

    @property
    def has_matches(self) -> bool:
        """Pass."""
        return all([bool(self.strings), bool(self.patterns)])

    @classmethod
    def load(
        cls,
        values: t.Optional[MatcherLoad],
        re_prefix: str = "~",
        split: bool = True,
        split_max: int = -1,
        split_sep: t.Optional[PatternLike] = SPLITTER,
        strip: bool = True,
        strip_chars: t.Optional[str] = None,
        hidden: t.Optional[str] = HIDDEN,
    ) -> "Matcher":
        """Load matcher values, return values as is if already Matcher obj.

        Args:
            values (t.Optional[MATCHER]): Matcher or values to parse into Matcher
            re_prefix (str, optional): prefix to use for regexes
            split (bool, optional): split values on split_sep
            split_max (int, optional): max number of splits to perform
            split_sep (t.Optional[PatternLike], optional): separator to split values on
            strip (bool, optional): strip values
            strip_chars (t.Optional[str], optional): chars to strip from values
            hidden (t.Optional[str], optional): token to use for hidden values

        Returns:
            Matcher: Matcher object
        """
        cls_args = dict(
            re_prefix=re_prefix,
            split=split,
            split_max=split_max,
            split_sep=split_sep,
            strip=strip,
            strip_chars=strip_chars,
            hidden=hidden,
        )
        if isinstance(values, cls):
            return cls(values=values.values, **cls_args)
        return cls(values=values, **cls_args)

    @cachetools.cached(cachetools.LRUCache(maxsize=CACHE_SIZE))
    def contains(self, value: str, patterns: bool = True) -> bool:
        """Check if value that contains strings or matches patterns.

        Args:
            value (str): value to check if any strs in self.strings are in
            patterns (bool, optional): check against self.patterns as well

        Returns:
            bool: True if any of self.strings in value or patterns=True and any of self.patterns
                matches value, False otherwise
        """
        value = coerce_str(value=value)
        for item in self.strings:
            if item in value:
                return True
        return self.search(value) if patterns else False

    @cachetools.cached(cachetools.LRUCache(maxsize=CACHE_SIZE))
    def equals(self, value: str, patterns: bool = True) -> bool:
        """Check if value that equals strings or matches patterns.

        Args:
            value (str): value to check if any strs in self.strings equals
            patterns (bool, optional): check against self.patterns as well

        Returns:
            bool: True if any of self.strings equals value or patterns=True and any of
                self.patterns matches value, False otherwise
        """
        value = coerce_str(value=value)
        for item in self.strings:
            if item == value:
                return True
        return self.search(value) if patterns else False

    @cachetools.cached(cachetools.LRUCache(maxsize=CACHE_SIZE))
    def search(self, value: str) -> bool:
        """Check if value that matches patterns.

        Args:
            value (str): value to check if any patterns in self.patterns match

        Returns:
            bool: True if any of self.patterns matches values, False otherwise
        """
        value = coerce_str(value=value)
        for item in self.patterns:
            if item.search(value):
                return True
        return False

    def hide_values(self, value: dict, patterns: bool = True) -> dict:
        """Hide values in value if keys match hide.

        Args:
            value (dict): dict to hide values of if any keys equal self.strings or match any
                self.patterns
            patterns (bool, optional): check against self.patterns as well

        Returns:
            dict: dict with matching keys values hidden
        """
        if is_str(value=self.hidden) and isinstance(value, dict):
            return {
                k: self.hidden if self.equals(value=coerce_str(value=k), patterns=patterns) else v
                for k, v in value.items()
            }
        return value

    def hide_lines(
        self,
        value: t.Union[bytes, str, t.List[str], t.Tuple[str]],
        patterns: bool = True,
        encoding: str = "utf-8",
        errors: str = "replace",
    ) -> t.List[str]:
        """Hide lines of a str that contain strings or match patterns.

        Args:
            value (t.Union[bytes, str, t.List[str], t.Tuple[str]]): value to splitlines if any of
                self.strings in value or self.patterns match
            patterns (bool, optional): check against self.patterns as well

        Returns:
            t.List[str]: value splitlines with lines as
                self.hidden if any matches to self.strings or self.patterns, elsewise original value
        """
        if isinstance(value, bytes):
            value = value.decode(encoding=encoding, errors=errors)
        if isinstance(value, str):
            value = value.splitlines()
        if is_str(value=self.hidden) and isinstance(value, (list, tuple)):
            return [
                self.hidden if self.contains(value=coerce_str(value=x), patterns=patterns) else x
                for x in value
            ]
        return value

    def matches(
        self, values: t.Union[str, t.List[str]], patterns: bool = True
    ) -> t.Tuple[t.List[str], t.List[PatternLike]]:
        """Get str or pattern matches of matches out of values.

        Args:
            values (t.Union[str, t.List[str]]): strs to check against self.strings or self.patterns
            patterns (bool, optional): check against self.patterns as well

        Returns:
            t.Tuple[t.List[str], t.List[PatternLike]]: list of matched and not matched values
        """

        def additem(item, target):
            if isinstance(item, (list, tuple)):
                for i in item:
                    additem(i, target)
            elif item not in target:
                target.append(item)

        values: t.List[str] = listify(value=values)
        matched: t.List[str] = []
        not_matched: t.List[PatternLike] = []

        for item in self.strings:
            target = matched if item in values else not_matched
            additem(item, target)

        if patterns:
            for item in self.patterns:
                item_matches = [x for x in values if item.search(x)]
                if item_matches:
                    additem(item_matches, matched)
                else:
                    additem(item, not_matched)

        return matched, not_matched

    def __str__(self) -> str:
        """Pass."""
        items = [
            f"split_sep={self.split_sep!r}",
            f"strings={self.strings!r}",
            f"patterns={self.patterns!r}",
        ]
        items = ", ".join(items)
        return f"Matcher({items})"

    def __repr__(self) -> str:
        """Pass."""
        return self.__str__()


def coerce_str(value: t.Any) -> str:
    """Coerce a value into a str.

    Args:
        value (t.Any): value to coerce to str.

    Returns:
        str: value coerced to str
    """
    value = bytes_to_str(value=value)
    if is_str(value=value):
        return value
    if value is None:
        return ""
    return str(value)
