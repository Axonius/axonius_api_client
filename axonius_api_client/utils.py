"""Utilities."""
import datetime
import logging
import re
import types
import typing as t

import bson
import dateutil.tz

# from .constants.general import EMPTY_VALUES, TRIM_POST
from .exceptions import DecodeError, FormatError, InvalidObjectIdError, InvalidTypeError

LOG: logging.Logger = logging.getLogger(__name__)

# XXX got moved from constants
SPLITTER: t.Pattern = re.compile(",")
"""Regex pattern to use for splitting strings that are CSV like."""

# XXX got moved from constants
TRUTHY_VALUES: t.List[t.Any] = (True, 1, "1", "true", "t", "yes", "y", "on")
"""Values that should be considered as truthy"""

# XXX got moved from constants
FALSEY_VALUES: t.Tuple[t.Any] = (False, 0, "0", "false", "f", "no", "n", "off")
"""Values that should be considered as falsey"""

# XXX got moved from constants
TRIM_POST: str = "... trimmed {removed_length} characters"
"""Value to add to end of trimmed string."""

# XXX got moved from constants
EMPTY_VALUES: t.Tuple[t.Any] = (None, list(), set(), dict(), "", "none", "null")
"""Values that should be considerd as empty."""


class CoerceStringBytes:
    """Defaults for :method:`coerce_str_if_bytes`."""

    encoding_format: str = "utf-8"
    encoding_errors: str = "strict"


def trim_value_repr(
    value: t.Any, max_length: t.Optional[int] = 30, trim_post: t.Optional[str] = TRIM_POST
) -> str:
    """Trim the value to a maximum length and appends info about the number of trimmed characters.

    Args:
        value (t.Any):
            The input value to be trimmed.
        max_length (t.Optional[int]):
            The maximum allowed length of the value repr.
        trim_post (t.Optional[str]):
            The string to add

    Returns:
        str:
            The trimmed value representation with info about the number of trimmed characters.
    """
    value_repr: str = repr(value)
    if isinstance(max_length, int) and max_length >= 0:
        original_length: int = len(value_repr)
        if original_length > max_length:
            value_repr: str = value_repr[:max_length]
            modified_length: str = len(value_repr)
            if isinstance(trim_post, str):
                removed_length: int = original_length - modified_length
                locals_dict: t.Dict[str, t.Any] = locals()
                try:
                    value_repr += trim_post.format(**locals_dict)
                except KeyError as exc:
                    raise FormatError(template=trim_post, error=exc, kwargs=locals_dict)
    return value_repr


def get_empties(value: t.Optional[t.Iterable] = ()) -> t.List[t.Any]:
    """Get a list of empty values.

    Args:
        value (t.Optional[t.Iterable]):
            Value to pass to :method:`merge_list_default`

    Returns:
        t.List[t.Any]:
            List of values to consider as empty.
    """
    return merge_list_default(value=value, default=EMPTY_VALUES)


def merge_list_default(
    value: t.Optional[t.Iterable] = (), default: t.Optional[t.Iterable] = ()
) -> t.List[t.Any]:
    """Merge a list with a default list if it is a list or tuple.

    Args:
        value (t.Optional[t.Iterable]):
            A list, tuple, set or anything.
        default (t.Optional[t.Iterable]):
            If value is list or tuple, Iterable to append to value.
            If value is not a list, tuple, or set, Iterable to return.

    Returns:
        t.List[t.Any]:
            If value is a list or tuple, return listify(value) + listify(default).
            If value is a set, return listify(value).
            Otherwise, return listify(default).

    """
    if isinstance(value, (list, tuple)):
        return listify(value) + listify(default)
    if isinstance(value, set):
        return listify(value)
    return listify(default)


def should_return_none(
    value: t.Optional[t.Any],
    allow_none: bool = False,
    allow_empty: bool = False,
    empties: t.Any = (),
) -> bool:
    """Check if a function should return None based on input value and provided flags.

    Args:
        value (t.Optional[t.Any]):
            The input value to check.
        allow_none (bool):
            If True, return True if the input value is None.
        allow_empty (bool):
            If True, return True if the input value forced into a lower-case
            stripped string is one of the values in check_empties (case-insensitive).
        empties (t.Any):
            A list, tuple, or set of values to check against when allow_empty is True.
            Set will use exactly the values provided. List or tuple will have :attr:`EMPTY_VALUES`
            added. If None or any other type, defaults to the :attr:`EMPTY_VALUES` list.

    Returns:
        bool:
            If the function should return None based on the input value and the flags, return True.
            Otherwise return False.
    """
    if value is None and allow_none:
        return True

    if allow_empty:
        empties: t.List[t.Any] = get_empties(value=empties)
        return value in empties or str(value).lower().strip() in empties

    return False


def uuid_str_to_datetime(
    value: t.Union[str, bytes],
    convert_to_utc: bool = True,
    allow_none: bool = False,
    allow_empty: bool = False,
    use_value: bool = False,
    encoding_format: str = CoerceStringBytes.encoding_format,
    encoding_errors: str = CoerceStringBytes.encoding_errors,
    value_fallback: t.Any = None,
    error_use_fallback: bool = True,
    log_error: bool = True,
    empties: t.Any = (),
) -> t.Union[datetime.datetime, t.Any]:
    """Convert bson.ObjectId or its string/byte string representation to datetime.datetime.

    Args:
        value (t.Union[str, bytes]):
            A string or byte string representation of a UUID genereated by bson.ObjectId.
        convert_to_utc (bool):
            If True, converts the datetime object's timezone to UTC.
        allow_none (bool):
            If True, return value_fallback if value is None
        allow_empty (bool):
            If True, return the value in value_fallback if the input value forced into a lower-case
            stripped string is one of :attr:`EMPTY_VALUES` (case-insensitive).
        value_fallback (t.Any):
            The value to return when any of allow_none, allow_empty, or error_use_fallback get
            triggered.
        use_value (t.Any):
            Return value instead of value_fallback when any of allow_none, allow_empty, or
            error_use_fallback get triggered.
        empties (t.Any):
            A list, tuple, or set of values to check against when allow_empty is True.
        encoding_format (str):
            If value is bytes, the encoding format to use when decoding into str.
        encoding_errors (str):
            If value is bytes, the error handling method to use when decoding into str.
        log_error (bool):
            If True and errors happen and error_use_fallback is False, log the error and any
            possible exception info to :attr:`LOG`.
        error_use_fallback (bool):
            If False, return value or value_fallback when errors happen.

    Returns:
        t.Optional[datetime.datetime]:
            A datetime.datetime object with UTC timezone offset (if convert_to_utc is True)
        t.Any:
            If any of these conditions happen,
            If allow_none is True and value is None, or error_use_fallback is False and an exception
            happens, or allow_empty is True and value is in empties, return value
            if use_value is True, otherwise return the value in value_fallback.

    Raises:
        InvalidTypeError:
            If value is not a str, bytes, or bson.ObjectId and error_use_fallback is True.
        InvalidObjectIdError:
            If value is str or bytes but is not a valid ObjectId and error_use_fallback is True.
        DecodeError:
            If value is bytes and decoding fails and error_use_fallback is True.
    """
    value_original: t.Any = value
    if should_return_none(
        value=value, allow_none=allow_none, allow_empty=allow_empty, empties=empties
    ):
        return handle_return(
            value=value_original, value_fallback=value_fallback, use_value=use_value
        )

    value = coerce_str_if_bytes(
        value=value, encoding_format=encoding_format, encoding_errors=encoding_errors
    )

    if isinstance(value, str):
        try:
            value: bson.ObjectId = bson.ObjectId(value)
        except bson.errors.InvalidId:
            error: Exception = InvalidObjectIdError(value=value)
            return handle_error(error)

    return uuid_bson_to_datetime()


def uuid_bson_to_datetime(
    value: bson.ObjectId,
    convert_to_utc: bool = True,
    allow_none: bool = False,
    allow_empty: bool = False,
    use_value: bool = False,
    value_fallback: t.Any = None,
    error_use_fallback: bool = True,
    log_error: bool = True,
    empties: t.Any = (),
) -> t.Union[datetime.datetime, t.Any]:
    """Convert bson.ObjectId or its string/byte string representation to datetime.datetime.

    Args:
        value (t.Union[str, bytes]):
            A string or byte string representation of a UUID genereated by bson.ObjectId.
        convert_to_utc (bool):
            If True, converts the datetime object's timezone to UTC.
        allow_none (bool):
            If True, return value_fallback if value is None
        allow_empty (bool):
            If True, return the value in value_fallback if the input value forced into a lower-case
            stripped string is one of :attr:`EMPTY_VALUES` (case-insensitive).
        value_fallback (t.Any):
            The value to return when any of allow_none, allow_empty, or error_use_fallback get
            triggered.
        use_value (t.Any):
            Return value instead of value_fallback when any of allow_none, allow_empty, or
            error_use_fallback get triggered.
        empties (t.Any):
            A list, tuple, or set of values to check against when allow_empty is True.
        encoding_format (str):
            If value is bytes, the encoding format to use when decoding into str.
        encoding_errors (str):
            If value is bytes, the error handling method to use when decoding into str.
        log_error (bool):
            If True and errors happen and error_use_fallback is False, log the error and any
            possible exception info to :attr:`LOG`.
        error_use_fallback (bool):
            If False, return value or value_fallback when errors happen.

    Returns:
        t.Optional[datetime.datetime]:
            A datetime.datetime object with UTC timezone offset (if convert_to_utc is True)
        t.Any:
            If allow_none is True and value is None, or error_use_fallback is False and an exception
            happens, or allow_empty is True and value is in empties, return value
            or value_fallback depending on use_value.

    Raises:
        InvalidTypeError:
            If value is not a str, bytes, or bson.ObjectId and error_use_fallback is True.
        InvalidObjectIdError:
            If value is str or bytes but is not a valid ObjectId and error_use_fallback is True.
        DecodeError:
            If value is bytes and decoding fails and error_use_fallback is True.
    """
    value_original: t.Any = value
    if should_return_none(
        value=value, allow_none=allow_none, allow_empty=allow_empty, empties=empties
    ):
        return handle_return(
            value=value_original, value_fallback=value_fallback, use_value=use_value
        )

    if not isinstance(value, bson.ObjectId):
        error: Exception = InvalidTypeError(value=value, allowed_types=bson.ObjectId)
        return handle_error(
            error=error,
            value=value,
            value_fallback=value_fallback,
            use_value=use_value,
            log_error=log_error,
            error_use_fallback=error_use_fallback,
        )

    dt: datetime.datetime = value.generation_time

    if convert_to_utc:
        dt: datetime.datetime = dt.astimezone(dateutil.tz.tzutc())

    return dt


def uuid_to_datetime(
    value: t.Optional[t.Union[str, bytes, bson.ObjectId]],
    convert_to_utc: bool = True,
    allow_none: bool = False,
    allow_empty: bool = False,
    use_value: bool = False,
    encoding_format: str = "utf-8",
    encoding_errors: str = "strict",
    value_fallback: t.Any = None,
    error_use_fallback: bool = True,
    log_error: bool = True,
    empties: t.Any = (),
) -> t.Union[datetime.datetime, t.Any]:
    """Convert bson.ObjectId or its string/byte string representation to datetime.datetime.

    Args:
        value (t.Optional[t.Union[str, bytes, bson.ObjectId]]):
            A bson.ObjectId instance, its string or byte string representation, or None.
        convert_to_utc (bool):
            If True, converts the datetime object's timezone to UTC.
        allow_none (bool):
            If True, return value_fallback if value is None
        allow_empty (bool):
            If True, return the value in value_fallback if the input value forced into a lower-case
            stripped string is one of :attr:`EMPTY_VALUES` (case-insensitive).
        value_fallback (t.Any):
            The value to return when any of allow_none, allow_empty, or error_use_fallback get
            triggered.
        use_value (t.Any):
            Return value instead of value_fallback when any of allow_none, allow_empty, or
            error_use_fallback get triggered.
        empties (t.Any):
            A list, tuple, or set of values to check against when allow_empty is True.
        encoding_format (str):
            If value is bytes, the encoding format to use when decoding into str.
        encoding_errors (str):
            If value is bytes, the error handling method to use when decoding into str.
        log_error (bool):
            If True and errors happen and error_use_fallback is False, log the error and any
            possible exception info to :attr:`LOG`.
        error_use_fallback (bool):
            If False, return value or value_fallback when errors happen.

    Returns:
        t.Optional[datetime.datetime]:
            A datetime.datetime object with UTC timezone offset (if convert_to_utc is True)
        t.Any:
            If any of these conditions happen,
            If allow_none is True and value is None, or error_use_fallback is False and an exception
            happens, or allow_empty is True and value is in empties, return value
            if use_value is True, otherwise return the value in value_fallback.

    Raises:
        InvalidTypeError:
            If value is not a str, bytes, or bson.ObjectId and error_use_fallback is True.
        InvalidObjectIdError:
            If value is str or bytes but is not a valid ObjectId and error_use_fallback is True.
        DecodeError:
            If value is bytes and decoding fails and error_use_fallback is True.
    """
    value_original: t.Any = value
    if should_return_none(
        value=value, allow_none=allow_none, allow_empty=allow_empty, empties=empties
    ):
        return handle_return(
            value=value_original, value_fallback=value_fallback, use_value=use_value
        )

    value = coerce_str_if_bytes(
        value=value, encoding_format=encoding_format, encoding_errors=encoding_errors
    )

    # make this a uuid_str_to_datetime
    if isinstance(value, str):
        try:
            value: bson.ObjectId = bson.ObjectId(value)
        except bson.errors.InvalidId:
            error: Exception = InvalidObjectIdError(value=value)
            return handle_error(error)
    # make this a uuid_str_to_datetime

    # make this uuid_bson_to_datetime
    if not isinstance(value, bson.ObjectId):
        error: Exception = InvalidTypeError(value=value, allowed_types=(str, bytes, bson.ObjectId))
        return handle_error(error)

    dt: datetime.datetime = value.generation_time

    if convert_to_utc:
        dt: datetime.datetime = dt.astimezone(dateutil.tz.tzutc())

    return dt
    # make this uuid_bson_to_datetime


def coerce_bool(
    value: t.Any,
    empties: t.Any = (),
    allow_none: bool = False,
    allow_empty: bool = False,
    value_fallback: t.Any = None,
    use_value: bool = False,
    encoding_format: str = "utf-8",
    encoding_errors: str = "strict",
) -> bool:
    """Convert an valueect into bool.

    Args:

    Raises:
        :exc:`ToolsError`: value is not able to be converted to bool
    """
    value_original: t.Any = value
    # XXX add exception if allow_none is False and value is None
    # XXX add exception if allow_empty is False and value in empties
    if should_return_none(
        value=value, allow_none=allow_none, allow_empty=allow_empty, empties=empties
    ):
        return handle_return(
            value=value_original, value_fallback=value_fallback, use_value=use_value
        )

    if value in [True, False]:
        return bool(value)

    # XXX make this common
    def combine(value):
        return ", ".join([f"{x!r}" for x in value])

    value: str = (
        str(
            coerce_str_if_bytes(
                value=value, encoding_format=encoding_format, encoding_errors=encoding_errors
            )
        )
        .lower()
        .strip()
    )

    if value in TRUTHY_VALUES:
        return True

    if value in FALSEY_VALUES:
        return False

    error: Exception = InvalidObjectIdError(value=value)
    return handle_error(error)

    # turn this into custom exception
    # need handle_error
    # msg = listify(errmsg)
    raise Exception(
        f"Supplied value {value_original!r} of type {get_type_str(value)} is not a valid boolean"
        f"  For True: {combine(TRUTHY_VALUES)}"
        f"  For False: {combine(FALSEY_VALUES)}"
    )


"""

class FieldMeta:

    is_unique: bool = False
    description: str = ""

"""


# TODO lots here
def coerce_str_if_bytes(
    value: t.Any,
    encoding_format: str = "utf-8",
    encoding_errors: str = "replace",
    error_use_fallback: bool = False,
    allow_none: bool = False,
    allow_empty: bool = False,
) -> t.Any:
    """Coerce value to str if it is bytes.

    Args:
        value (t.Any):
            Value to coerce to bytes if it is a str
        encoding_format (str):
            encoding to use as value.decode(encoding, errors=encoding_errors)
        encoding_errors (str):
            errors to use as value.decode(encoding, errors=encoding_errors)
    """
    if isinstance(value, bytes):
        try:
            return value.decode(encoding_format, errors=encoding_errors)
        except UnicodeDecodeError:
            error: Exception = DecodeError(
                value=value, encoding_format=encoding_format, errors=encoding_errors
            )
            raise error
    return value


def listify(
    value: t.Any = None,
    split: bool = False,
    split_max: int = -1,
    splitter: t.Optional[t.Union[str, t.Pattern]] = SPLITTER,
    strip: bool = False,
    strip_value: t.Optional[str] = None,
    empties_clean: bool = False,
    empties: t.Any = (),
    encoding_format: str = "utf-8",
    encoding_errors: str = "replace",
) -> list:
    """Force an object into a list.

    Notes:
        * :obj:`list` or :obj:`types.GeneratorType` - returns as is
        * :obj:`None` - returns as an empty list
        * :obj:`tuple` or :obj:`set` - convert to list
        * otherwise return as a list of obj

    Args:
        value: object to coerce to list
    """
    if isinstance(value, (types.GeneratorType, list)):
        return value
    if value is None:
        return []
    if isinstance(value, (tuple, set)):
        return list(value)

    if split:
        value = coerce_str_if_bytes(
            value=value, encoding_format=encoding_format, encoding_errors=encoding_errors
        )
        # TODO: move this to function
        if isinstance(value, str):
            if isinstance(splitter, t.Pattern):
                split_max = 0 if split_max == -1 else split_max
                value: t.List[str] = splitter.split(value, maxsplit=split_max)
            else:
                value: t.List[str] = value.split(sep=splitter, maxsplit=split_max)

    if strip:
        value: t.List[str] = [x.strip(strip_value) for x in value if isinstance(x, str)]
    # TODO: empties_clean()
    # TODO: finish this, need merge_list_default(value=empties, default=EMPTY_VALUES)
    return value
    return [value]
