# -*- coding: utf-8 -*-
"""Parser for datetime or delta strings."""
import dataclasses
import typing as t
import random
import re
import datetime
import logging

import dateutil
import dateutil.tz
import dateutil.parser
from ..tools import listify
from ..data import BaseEnum

LOG: logging.Logger = logging.getLogger(__name__)
EMPTY: t.Iterable[t.Any] = ("null", "none", None, "")
ENCODING: str = "utf-8"
ERROR_ENCODING: str = "ignore"
TZ: t.Union[str, bytes, datetime.tzinfo] = datetime.timezone.utc
MARKERS_NOW: t.Tuple[str, ...] = ("now", "today", "current")
MARKERS_DELTA: t.ClassVar[t.Tuple[str, ...]] = ("~", "delta")
MARKERS_HELP: t.ClassVar[t.Tuple[str, ...]] = ("help", "?", "docs")


def bytes_to_str(value: t.Any, encoding: str = ENCODING, errors: str = ERROR_ENCODING) -> t.Any:
    """Convert value to str if value is bytes.

    Args:
        value (t.Any): value to convert to str
        encoding (str, optional): encoding to use
        errors (str, optional): how to handle errors

    Returns:
        t.Any: str if value is bytes, else original value
    """
    return value.decode(encoding=encoding, errors=errors) if isinstance(value, bytes) else value


def get_now() -> datetime.datetime:
    """Get current datetime in UTC.

    Returns:
        datetime.datetime: current datetime in UTC
    """
    return datetime.datetime.utcnow().astimezone(datetime.timezone.utc)


def str_to_float(value: str) -> float:
    """Coerce duration from a string into a float."""
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid float in value {value!r} - {exc}")


def re_escape(value: t.Any) -> str:
    """Escape value for use in regex.

    Args:
        value: value to escape

    Returns:
        escaped value
    """
    value = bytes_to_str(value=value)
    value = str(value) if not isinstance(value, str) else value
    return re.escape(value)


def re_join(*args: t.Any) -> str:
    """Join args into a regex pattern.

    Args:
        *args: args to join into regex | pattern

    Returns:
        str: | joined args for use in a regex pattern
    """
    return r"|".join(re_escape(x) for x in args)


def is_empty(value: t.Any, empty: t.Iterable[t.Any] = EMPTY) -> bool:
    """Check if value is empty.

    Args:
        value: value to check
        empty: tuple of values to check if value is in

    Returns:
        bool: True if value is empty, False otherwise
    """
    if isinstance(value, (str, bytes)):
        check: str = bytes_to_str(value).strip().lower()
    else:
        check: str = str(value).strip().lower()
    return not bool(check) or check in listify(empty)


def should_return_none(
    value: t.Any = None,
    allow_none: bool = False,
    allow_empty: bool = False,
    empty: t.Iterable[t.Any] = EMPTY,
) -> bool:
    """Check if function should return None.

    Args:
        value: value to check
        allow_none: if True, return True if value is None
        allow_empty: if True, return True if value is empty
        empty: if allow_empty is True, check if value is in this tuple

    Returns:
        bool: True if function should return None, False otherwise
    """
    if allow_none and value is None:
        return True
    if allow_empty and is_empty(value=value, empty=empty):
        return True
    return False


def random_float(
    minimum: t.Union[int, float] = 1,
    maximum: t.Union[int, float] = 10,
    places: t.Optional[int] = 2,
) -> float:
    """Generate a random float.

    Args:
        minimum: minimum value
        maximum: maximum value
        places: number of decimal places to round to

    Returns:
        random float
    """
    return round(random.uniform(minimum, maximum), places)


def log_exc_or_ret(
    exc: t.Optional[Exception] = None,
    error_log: bool = True,
    error_raise: bool = True,
    as_none: t.Any = None,
) -> t.Any:
    """Raise exception or log error or return None.

    Args:
        exc: exception to raise
        error_log: if true, log exception to LOG
        error_raise: if true, raise exception
        as_none: value to return
    """
    if error_log:
        log_method: t.Callable = LOG.exception if error_raise else LOG.debug
        log_method(
            f"Exception={type(exc)}, as_none={as_none}, error_raise={error_raise}, {exc}",
            exc_info=True,
        )
    if error_raise and isinstance(exc, Exception):
        raise exc
    return as_none


def get_tz(
    value: t.Optional[t.Union[str, bytes, datetime.tzinfo]] = None,
    error_raise: bool = True,
    error_log: bool = True,
    allow_none: bool = False,
    allow_empty: bool = False,
    empty: t.Iterable[t.Any] = EMPTY,
    as_none: t.Any = None,
) -> t.Optional[datetime.tzinfo]:
    """Get tzinfo from a string or tzinfo object.

    Args:
        value: string or tzinfo object
        error_raise: raise ValueError if value is not a valid timezone
        error_log: log error if value is not a valid timezone
        allow_none: return None if value is None
        allow_empty: raise ValueError if value is empty
        empty: empty values to check against
        as_none: value to return if value is not str,bytes, or tzinfo or if an error happens

    Returns:
        tzinfo object
    """
    if should_return_none(allow_none=allow_none, allow_empty=allow_empty, value=value, empty=empty):
        return as_none

    if isinstance(value, datetime.tzinfo):
        return value

    if isinstance(value, (str, bytes)):
        check: str = bytes_to_str(value=value).strip()
        if not check:
            exc: ValueError = ValueError(f"Timezone is empty {value!r}")
            return log_exc_or_ret(
                exc=exc, error_log=error_log, error_raise=error_raise, as_none=as_none
            )

        tz: t.Optional[datetime.tzinfo] = dateutil.tz.gettz(check)
        if not isinstance(tz, datetime.tzinfo):
            exc: ValueError = ValueError("Invalid timezone {value!r}")
            return log_exc_or_ret(
                exc=exc, error_log=error_log, error_raise=error_raise, as_none=as_none
            )
        return tz

    exc: TypeError = TypeError(
        f"Timezone is not str, bytes, or tzinfo - is type {type(value)} value {value!r}"
    )
    return log_exc_or_ret(exc=exc, error_log=error_log, error_raise=error_raise, as_none=as_none)


def as_timezone(
    value: datetime.datetime,
    tz: t.Optional[t.Union[str, bytes, datetime.tzinfo]] = TZ,
    error_raise: bool = True,
    error_log: bool = True,
    allow_none: bool = False,
    allow_empty: bool = False,
    empty: t.Iterable[t.Any] = EMPTY,
    as_none: t.Any = None,
) -> datetime.datetime:
    """Get a datetime as a different timezone.

    Args:
        value: datetime object
        tz: if not None, replace tzinfo with this value
        error_raise: raise ValueError if tz is not a valid timezone
        error_log: log error if tz is not a valid timezone
        allow_none: return None if tz is None
        allow_empty: raise ValueError if tz is empty
        empty: empty values to check tz against
        as_none: value to return if value is not str,bytes, or tzinfo or if an error happens

    Returns:
        datetime.datetime: datetime object with replaced tzinfo
    """
    tz: t.Optional[datetime.tzinfo] = get_tz(
        value=tz,
        error_raise=error_raise,
        error_log=error_log,
        allow_none=allow_none,
        allow_empty=allow_empty,
        empty=empty,
        as_none=as_none,
    )
    return value.astimezone(tz) if isinstance(tz, datetime.tzinfo) else value


def parse_dt(
    value: t.Union[str, bytes],
    error_log: bool = True,
    error_raise: bool = True,
    as_none: t.Any = None,
    fuzzy: bool = True,
    markers_now: t.Optional[t.Iterable[str]] = MARKERS_NOW,
) -> t.Optional[datetime.datetime]:
    """Parse a datetime string.

    Args:
        value: datetime string
        error_log: log error if value is not a valid datetime
        error_raise: raise error if value is not a valid datetime
        as_none: value to return if value is not a valid datetime
        fuzzy: if true, allow fuzzy parsing
        markers_now: list of strings to return get_now() for


    Returns:
        datetime.datetime: parsed datetime
    """
    value = bytes_to_str(value)
    if (isinstance(markers_now, (list, tuple)) and markers_now) and (
        isinstance(value, str) and value.strip().lower() in markers_now
    ):
        return get_now()
    # noinspection PyBroadException
    try:
        return dateutil.parser.parse(bytes_to_str(value), fuzzy=fuzzy)
    except Exception as exc:
        return log_exc_or_ret(
            exc=exc, error_log=error_log, error_raise=error_raise, as_none=as_none
        )


NOW: datetime.datetime = get_now()


RE_DELTA_UNITS: t.ClassVar[t.Pattern] = re.compile(
    r"""
    ((?P<value>[-+]?\d*\.?\d+)       # Match the value (integer or float)
    (?P<unit>[a-zA-Z]+))             # Match the unit (letters)
    |                                # OR
    ((?P<unit2>[a-zA-Z]+)            # Match the unit (letters)
    \s*=\s*                          # Match the equal sign, possibly surrounded by spaces
    (?P<value2>[-+]?\d*\.?\d+))      # Match the value (integer or float)
""",
    re.VERBOSE,
)
RE_DATETIME_DELTA: t.ClassVar[t.Pattern] = re.compile(
    rf"""
    (?P<datetime>.*?)         # Match optional datetime part
    (?P<marker>{re_join(*MARKERS_DELTA)}+) # Match optional delta marker
    (?P<delta>.*)             # Match optional delta part
    """,
    re.VERBOSE | re.I,
)

EXAMPLES: t.Dict[str, str] = {
    "2019-01-01": "2019-01-01 00:00:00+00:00",
    "February 2 2023 3:24": "2023-02-02 03:24:00+00:00",
    "2pm EDT": "2023-04-04 18:00:00+00:00",
    **{f"{x}": f"{NOW}" for x in MARKERS_NOW},
    "now ~ 1 day": f"{NOW - datetime.timedelta(days=1)}",
    "~ hours=-1 days=1": f"{NOW - datetime.timedelta(hours=-1, days=1)}",
}


def parse_datetime(
    value: t.Optional[t.Union[str, bytes, datetime.datetime]],
    error_raise: bool = True,
    error_log: bool = True,
    allow_none: bool = False,
    allow_empty: bool = False,
    empty: t.Iterable[t.Any] = EMPTY,
    as_none: t.Any = None,
    fuzzy: bool = True,
    markers_now: t.Optional[t.Iterable[str]] = MARKERS_NOW,
    as_tz: t.Optional[t.Union[str, bytes, datetime.tzinfo]] = datetime.timezone.utc,
) -> t.Optional[datetime.datetime]:
    """Parse datetime from value.

    Args:
        value: value to parse
        error_raise: raise ValueError if value is not a valid datetime
        error_log: log error if value is not a valid datetime
        allow_none: return None if value is None
        allow_empty: raise ValueError if value is empty
        empty: empty values to check value against
        as_none: value to return if value is not str,bytes, or tzinfo or if an error happens
        fuzzy: if True, allow fuzzy parsing
        markers_now: list of strings to return datetime.utcnow() for
        as_tz: if not None, replace tzinfo with this value

    Returns:
        datetime object
    """
    if should_return_none(value=value, allow_none=allow_none, allow_empty=allow_empty, empty=empty):
        dt = as_none
    elif isinstance(value, datetime.datetime):
        dt = value
    elif isinstance(value, (str, bytes)):
        dt = parse_dt(
            value=value,
            error_log=error_log,
            error_raise=error_raise,
            as_none=as_none,
            fuzzy=fuzzy,
            markers_now=markers_now,
        )
    else:
        exc: TypeError = TypeError(
            f"Value is not str, bytes, or datetime - is type {type(value)} value {value!r}"
        )
        dt = log_exc_or_ret(exc=exc, error_log=error_log, error_raise=error_raise, as_none=as_none)
    return as_timezone(
        value=dt,
        tz=as_tz,
        error_raise=error_raise,
        error_log=error_log,
        allow_none=allow_none,
        empty=empty,
        as_none=as_none,
    )


def parse_timedelta(
    value: t.Union[str, bytes],
    error_raise: bool = True,
    error_log: bool = True,
    allow_none: bool = False,
    allow_empty: bool = False,
    empty: t.Iterable[t.Any] = EMPTY,
    as_none: t.Any = None,
) -> t.Optional[t.Dict[str, float]]:
    """Extract units and their durations from a string.

    Args:
        value: string to extract from
        error_raise: raise ValueError when parsing errors happen
        error_log: log parsing errors
        allow_none: return None if value is None
        allow_empty: raise ValueError if value is empty
        empty: empty values to check value against
        as_none: value to return if errors happen and error_raise is False
    """
    if should_return_none(value=value, allow_none=allow_none, allow_empty=allow_empty, empty=empty):
        return as_none

    value = bytes_to_str(value=value)
    matches: t.Iterator[t.Match] = RE_DATETIME_DELTA.finditer(value)
    if not matches and not allow_empty:
        exc: ValueError = ValueError(f"Value is not a valid delta string - {value!r}")
        return log_exc_or_ret(
            exc=exc, error_log=error_log, error_raise=error_raise, as_none=as_none
        )

    deltas: t.Dict[str, float] = {}
    for match in matches:
        try:
            unit = DeltaUnits.get_unit(value=match.group("unit"))
            duration = str_to_float(value=match.group("duration"))
        except ValueError as exc:
            # TODO: need to rebuild help string with examples
            if error_raise:
                raise ValueError(f"Invalid delta string - {value!r}") from exc
        else:
            deltas[unit] = duration
    return deltas


class DeltaUnits(BaseEnum):
    """Enum for delta units."""

    days: t.List[str] = ["days", "day", "d"]
    seconds: t.List[str] = ["seconds", "second", "secs", "sec", "s"]
    microseconds: t.List[str] = ["microseconds", "microsecond", "usecs", "usec", "us"]
    milliseconds: t.List[str] = ["milliseconds", "millisecond", "msecs", "msec", "ms"]
    minutes: t.List[str] = ["minutes", "minute", "min", "m"]
    hours: t.List[str] = ["hours", "hour", "hrs", "hr", "h"]
    weeks: t.List[str] = ["weeks", "week", "wks", "wk", "w"]

    @property
    def enum_help(self):
        """Get a string describing this enum."""
        return f"{self.name} (alternates: {', '.join(self.value)})"

    @classmethod
    def get_unit(cls, value: str) -> str:
        """Coerce a unit from a string into a valid enum name."""
        for enum in cls:
            if value in enum.value:
                return enum.name
        raise ValueError(f"Invalid unit in {value!r}")


@dataclasses.dataclass()
class DateDeltaParser:
    """Parser for datetime or delta strings."""

    value: t.Optional[t.Union[str, bytes]] = None
    """Value to parse."""

    match: t.ClassVar[t.Optional[t.Match]] = None
    """Match object."""

    is_match: t.ClassVar[bool] = False
    """If value_check matches pattern."""

    groups: t.ClassVar[dict] = None
    """Groups from match object."""

    def __post_init__(self):
        """Post init."""
        self.value: str = bytes_to_str(self.value)
        self.match: t.ClassVar[t.Optional[t.Match]] = RE_DATETIME_DELTA.search(self.value)
        self.is_match: t.ClassVar[bool] = bool(self.match)
        self.groups: t.ClassVar[dict] = self.match.groupdict() if self.is_match else {}

    def get_datetime(
        self,
        error_raise: bool = True,
        allow_none: bool = False,
        allow_empty: bool = False,
        allow_empty_delta: bool = False,
        empty: t.Iterable[t.Any] = EMPTY,
        as_none: t.Any = None,
        markers_now: t.Optional[t.Iterable[str]] = MARKERS_NOW,
        as_tz: t.Optional[t.Union[str, bytes, datetime.tzinfo]] = None,
    ) -> t.Optional[datetime.datetime]:
        """Get datetime from value."""
        if not self.is_match:
            return parse_datetime(
                value=self.value,
                error_raise=error_raise,
                allow_none=allow_none,
                allow_empty=allow_empty,
                empty=empty,
                as_none=as_none,
                markers_now=markers_now,
                as_tz=as_tz,
            )
        else:
            start: datetime.datetime = parse_datetime(
                value=self.match_datetime,
                error_raise=error_raise,
                allow_none=True,
                allow_empty=True,
                empty=empty,
                as_none=get_now(),
                markers_now=markers_now,
                as_tz=as_tz,
            )
            print(f"start={start!r}")
            delta: t.Optional[datetime.timedelta] = parse_timedelta(
                value=self.match_delta,
                error_raise=error_raise,
                allow_none=allow_empty_delta,
                allow_empty=allow_empty_delta,
                empty=empty,
                as_none=None,
            )
            print(f"delta={delta!r}")

            # delta: t.Optional[datetime.timedelta] = parse_timedelta(
            #     value=self.match_delta,
            #     error_raise=error_raise,
            #     allow_none=True,
            #     allow_empty=True,
            #     empty=empty,
            #     as_none=None,
            # )
            # print(f"delta={delta!r}")

    @property
    def match_datetime(self) -> t.Optional[str]:
        """Get datetime from value."""
        return self.groups.get("datetime")

    @property
    def match_marker(self) -> t.Optional[str]:
        """Get marker from value."""
        return self.groups.get("marker")

    @property
    def match_delta(self) -> t.Optional[str]:
        """Get delta from value."""
        return self.groups.get("delta")

    def __str__(self) -> str:
        """Get str representation."""
        items: t.List[str] = [
            f"value={self.value!r}",
            f"is_match={self.is_match!r}",
            f"match_datetime={self.match_datetime!r}",
            f"match_marker={self.match_marker!r}",
            f"match_delta={self.match_delta!r}",
        ]
        items: str = ", ".join(items)
        return f"{self.__class__.__name__}({items})"
