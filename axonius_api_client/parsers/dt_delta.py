# -*- coding: utf-8 -*-
"""Parser for datetime or delta strings."""
import typing as t
import random
import re
import datetime

import dateutil

import dateutil.parser
from ..tools import echo_debug
from ..data import BaseEnum

DELTA_MARKER: str = "delta"
DELTA_RE: t.Pattern = re.compile(f"{DELTA_MARKER}", re.I)
NOW_MARKER: str = "now"
NOW_RE: t.Pattern = re.compile(f"{NOW_MARKER}", re.I)
EXAMPLES: t.Dict[str, str] = {
    "2019-01-01": "2019-01-01 00:00:00+00:00",
    "February 2 2023 03:24:00": "2023-02-02 03:24:00+00:00",
    "now": "2023-04-04 19:26:00.318512+00:00",
    "2pm EDT": "2023-04-04 18:00:00+00:00",
}
EMPTY_STRINGS: t.Tuple[str, str] = ("null", "none")


class Resolutions(BaseEnum):
    """Enum for delta resolution."""

    days: t.List[str] = ["days", "day", "d"]
    seconds: t.List[str] = ["seconds", "second", "secs", "sec", "s"]
    microseconds: t.List[str] = ["microseconds", "microsecond", "usecs", "usec", "us"]
    milliseconds: t.List[str] = ["milliseconds", "millisecond", "msecs", "msec", "ms"]
    minutes: t.List[str] = ["minutes", "minute", "min", "m"]
    hours: t.List[str] = ["hours", "hour", "hrs", "hr", "h"]
    weeks: t.List[str] = ["weeks", "week", "wks", "wk", "w"]

    @classmethod
    def get_examples(cls) -> t.List[str]:
        """Get examples of how to use this enum."""
        ret: t.List[str] = []
        resolutions = list(cls)
        random.shuffle(resolutions)
        selected_resolutions = resolutions[: random.randint(3, 5)]
        format1 = ", ".join(
            f"{random.choice(resolution.value)}={round(random.uniform(1, 10), 2)}"
            for resolution in selected_resolutions
        )
        format2 = " ".join(
            f"{round(random.uniform(1, 10), 2)}{random.choice(resolution.value)}"
            for resolution in selected_resolutions
        )
        ret.append(f"{DELTA_MARKER} {format1}")
        ret.append(f"{DELTA_MARKER} {format2}")
        return ret

    @property
    def enum_info(self):
        """Get a string describing this enum."""
        return f"{self.name} (alternates: {', '.join(self.value)})"

    @classmethod
    def get_help(cls, msg: t.Optional[str] = None):
        """Get help for this enum."""
        examples: t.List[str] = cls.get_examples()
        ret: t.List[str] = [msg] if msg else []
        ret += [
            "Valid delta resolutions:",
            *[f"  {x.enum_info}" for x in cls],
            "",
            "Example delta resolutions:",
            *[f"  {x}" for x in examples],
            "",
            "Example date strings:",
            *[f"  {k} becomes {v}" for k, v in EXAMPLES.items()],
        ]
        return "\n".join(ret)

    @staticmethod
    def parse_resolution_duration(value: str) -> t.Tuple[str, str]:
        """Parse a string into a datetime.timedelta arguments."""
        if "=" in value:
            resolution, duration = [x.strip() for x in value.strip().lower().split("=", 1)]
            resolution = "".join(x for x in resolution if x.isalpha())
            duration = "".join(x for x in duration if x.isdigit() or x in [".", "-"])
        else:
            resolution, duration = ("", "")
            negative = False
            dot = False
            for character in value:
                if character.isalpha():
                    resolution += character.lower()
                elif character.isdigit():
                    duration += character
                elif character == "." and not dot:
                    duration += character
                    dot = True
                elif character == "-" and not negative:
                    negative = True
                    duration = character + duration
        return resolution, duration

    @classmethod
    def get_resolution(cls, value: str) -> str:
        """Pass."""
        for enum in cls:
            if value in enum.value:
                return enum.name
        raise ValueError(cls.get_help(f"Invalid resolution in {value!r}"))

    @classmethod
    def get_duration(cls, value: str) -> t.Union[int, float]:
        """Pass."""
        try:
            return float(value) if "." in value else int(value)
        except ValueError:
            raise ValueError(cls.get_help(f"Invalid integer or float in value {value!r}"))

    @classmethod
    def parse(
        cls,
        value: t.Union[str, bytes],
        bytes_encoding: str = "utf-8",
        bytes_errors: str = "ignore",
    ) -> t.Tuple[str, t.Union[int, float]]:
        """Extract resolution and duration from a string.

        Args:
            value: string to extract from
            bytes_encoding: encoding to use if value is bytes
            bytes_errors: errors to use if value is bytes

        Returns:
            tuple of resolution and duration
        """
        if isinstance(value, bytes):
            value: str = value.decode(bytes_encoding, bytes_errors)

        resolution, duration = cls.parse_resolution_duration(value=value)
        resolution = cls.get_resolution(value=resolution)
        duration = cls.get_duration(value=duration)
        return resolution, duration


def parse_delta(
    value: t.Union[str, bytes],
    error: bool = True,
    echo: bool = False,
    delta_re: t.Pattern = DELTA_RE,
    bytes_encoding: str = "utf-8",
    bytes_errors: str = "ignore",
) -> t.Dict[str, t.Union[int, float]]:
    """Parse a string into a datetime.timedelta arguments.

    Notes:
        Supported formats:
            - ``1d``
            - ``66s``
            - ``1d 2h 3m 4s``
            - ``1d,2h,3m,4s``
            - ``days=1,hours=2,minutes=3,secs=4``
            - ``days=1 hours=2 3min secs=4``

    Args:
        value: string to parse
        error: raise error on failure
        echo: echo error on failure
        delta_re: string to remove from value if found
        bytes_encoding: encoding to use if value is bytes
        bytes_errors: errors to use if value is bytes

    Returns:
        t.Dict[str, t.Union[int, float]]: dict of resolution and duration,
            suitable for passing into ``datetime.timedelta(**deltas)``
    """
    if isinstance(value, bytes):
        value: str = value.decode(bytes_encoding, bytes_errors)

    value = delta_re.sub("", value).strip()

    if "," in value:
        deltas: t.List[str] = value.split(",")
    else:
        deltas: t.List[str] = value.split()

    count: int = len(deltas)
    ret: t.Dict[str, t.Union[int, float]] = {}
    for idx, delta in enumerate(deltas):
        if not delta.strip():
            continue
        try:
            resolution, duration = Resolutions.parse(delta)
        except Exception as exc:
            msgs: t.List[str] = [
                f"Unable to parse delta #{idx +1}/{count}: {delta!r}",
                f"While parsing value: {value!r}",
                f"{exc}",
            ]
            msg: str = "\n".join(msgs)
            if error:
                raise ValueError(msg)
            echo_debug(msg, echo=echo)
            continue
        ret[resolution] = duration
    return ret


def is_empty(value: t.Any, empty_strings: t.Tuple[str] = EMPTY_STRINGS) -> bool:
    """Check if value is empty."""
    if not value:
        return True
    if isinstance(value, (str, bytes)):
        if isinstance(value, bytes):
            value: str = value.decode("utf-8", "ignore")
        return not bool(value.strip()) or value.lower() in empty_strings
    return not bool(value)


def should_return_none(
    value: t.Any = None,
    allow_none: bool = False,
    allow_empty: bool = False,
    empty_strings: t.Tuple[str] = EMPTY_STRINGS,
) -> bool:
    """Check if value should return None."""
    return (value is None and allow_none) or (
        allow_empty and is_empty(value=value, empty_strings=empty_strings)
    )


def parse_dt_or_delta(
    value: t.Union[str, bytes],
    delta_re: t.Pattern = DELTA_RE,
    bytes_encoding: str = "utf-8",
    bytes_errors: str = "ignore",
    tz_replace: t.Optional[datetime.tzinfo] = datetime.timezone.utc,
    allow_none: bool = False,
    allow_empty: bool = False,
    empty_strings: t.Tuple[str] = EMPTY_STRINGS,
    as_none: t.Any = None,
) -> t.Optional[datetime.datetime]:
    """Parse a datetime or delta string."""
    if should_return_none(
        value=value, allow_none=allow_none, allow_empty=allow_empty, empty_strings=empty_strings
    ):
        return as_none

    if isinstance(value, bytes):
        value = value.decode(bytes_encoding, bytes_errors)
    if delta_re.search(value):
        deltas: t.Dict[str, t.Union[int, float]] = parse_delta(value=value)
        now: datetime.datetime = datetime.datetime.utcnow()
        value = now - datetime.timedelta(**deltas) if any(deltas.values()) else now
    elif value.strip().lower() == NOW_MARKER:
        value = datetime.datetime.utcnow()
    else:
        try:
            value = dateutil.parser.parse(value)
        except Exception as exc:
            raise ValueError(
                f"Unable to parse datetime from value {value!r}: {exc}\n"
                f"{Resolutions.get_help()}"
            )
    if isinstance(tz_replace, datetime.tzinfo):
        value = value.astimezone(tz_replace)
    return value
