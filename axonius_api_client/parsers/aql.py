"""Parsers for AQL."""
import re
import types
import typing as t

from axonius_api_client.constants.fields import AXID
from axonius_api_client.projects.cf_token.tools import listify


def to_str(
    value: t.Any,
    callback_coerce: t.Optional[callable] = None,
    callback_coerce_error: bool = False,
    expected_type: t.Any = str,
    strip: bool = True,
    encoding: str = "utf-8",
    encoding_errors: str = "ignore",
    **kwargs,
) -> t.Optional[str]:
    """Coerce a value to a string.

    Args:
        value: value to coerce
        callback_coerce: function to call to coerce `value`
        callback_coerce_error: True=raise errors from `callback_coerce`
        strip: True=strip whitespace from `value` before `callback_coerce`
        expected_type: type to expect after `callback_coerce`
        encoding: encoding to use to decode `value` if it is bytes
        encoding_errors: errors to use to decode `value` if it is bytes
        **kwargs: passed to `callback_coerce`
    """
    if isinstance(value, bytes):
        value = value.decode(encoding=encoding, errors=encoding_errors)
    if strip and isinstance(value, str):
        value = value.strip()
    if callable(callback_coerce):
        try:
            value = callback_coerce(value, **kwargs)
        except Exception:
            if callback_coerce_error:
                raise
    return None if (expected_type and not isinstance(value, expected_type)) else value


def coerce_pattern(
    value: t.Any,
    pattern_prefix: t.Optional[str] = "~",
    prefix_strip: t.Optional[int] = None,
    pattern_flags: t.Optional[int] = re.IGNORECASE,
    **kwargs,
) -> t.Optional[t.Union[str, t.Pattern]]:
    """Coerce a value to a string or regex pattern.

    Args:
        value: value to coerce
        pattern_prefix: prefix to use to indicate a regex pattern
        prefix_strip: length to strip from `value` before compiling pattern, `len(pattern_prefix)`
        pattern_flags: flags to use when compiling pattern
        kwargs: passed to `re.compile`

    Returns:
        str: value if it is a string
        pattern: pattern if it is a pattern already or a string that starts with `pattern_prefix`
        None: if it is not a string or a string that starts with `pattern_prefix` or a pattern
    """
    if isinstance(value, t.Pattern):
        return value
    if isinstance(value, str):
        if isinstance(pattern_prefix, str) and pattern_prefix:
            if value.startswith(pattern_prefix):
                if not isinstance(prefix_strip, int):
                    prefix_strip = len(pattern_prefix)
                return re.compile(value[prefix_strip:], pattern_flags)
        if value:
            return value
    return None


def to_str_pattern(
    value: t.Any,
    callback_coerce: t.Optional[callable] = coerce_pattern,
    callback_coerce_error: bool = False,
    expected_type: t.Any = (str, t.Pattern),
    strip: bool = True,
    encoding: str = "utf-8",
    encoding_errors: str = "ignore",
    **kwargs,
) -> t.Optional[t.Union[str, t.Pattern]]:
    """Coerce a value to a string or regex pattern.

    Args:
        value: value to coerce
        callback_coerce: function to call to coerce `value`
        callback_coerce_error: True=raise errors from `callback_coerce`
        strip: True=strip whitespace from `value` before `callback_coerce`
        expected_type: type to expect after `callback_coerce`
        encoding: encoding to use to decode `value` if it is bytes
        encoding_errors: errors to use to decode `value` if it is bytes
        **kwargs: passed to `callback_coerce`
    """
    return to_str(
        value=value,
        callback_coerce=callback_coerce,
        callback_coerce_error=callback_coerce_error,
        expected_type=expected_type,
        strip=strip,
        encoding=encoding,
        encoding_errors=encoding_errors,
        **kwargs,
    )


def extract_key_values(value: t.Dict, keys: t.Optional[t.Sequence[str]] = None) -> t.List[t.Any]:
    """Extract key values from a value.

    Args:
        value: value to extract from
        keys: keys to extract from value, if None then all keys are used

    Returns:
        list: list of values found
    """
    keys = listify(keys)
    # TODO need a way to hunt for all sorts of keys: mixed case and different variations of
    # name and accidental quotes still around names
    # TODO: keys should just be re.compile('internal_axon_id|Asset Unique ID', re.I)

    """
    let's think about this
    when assets come back from the api, they each have an 'internal_axon_id' key
    when assets are exported to CSV by the API or the API client, they have any of the following: 
        'internal_axon_id'
        'Aggregated: Asset Unique ID'
        'Asset Unique ID'
        'agg:internal_axon_id'
        
    
    we want to be able to support the following:
    keys = ['internal_axon_id', 'Aggregated: Asset Unique ID', 'Asset Unique ID', 
        'agg:internal_axon_id']

    key_matches = [k for k in keys_in_value if any([p.search(k) for p in key_patterns])]
    """
    return [value[x] for x in keys if x in value] if keys else list(value.values())


def extract_strs(
    *args: t.Union[str, bytes, list, tuple, set, types.GeneratorType, dict],
    handle_dict: bool = True,
    keys: t.Optional[t.Sequence[str]] = None,
    split: bool = False,
    callback_exclude: t.Optional[t.Callable] = None,
    recursion_level: t.Optional[int] = None,
    recursion_max: t.Optional[int] = 4,
    **kwargs,
) -> t.List[str]:
    """Recursively find all non-empty strings.

    Args:
        *args: values to find strings in
        handle_dict: True=extract values from dicts, False=ignore dicts
        keys: keys to find strings in if `args` is a dict or csv, if None then all keys are used
        split: True=split strings on newlines and try to find strings in the split
        callback_exclude: callback to use to exclude values from being returned
        recursion_level: current level of recursion
        recursion_max: max level of recursion (2 should support list of dicts)
        **kwargs: passed to `to_str`

    Returns:
        list: list of strings found
    """
    first = not isinstance(recursion_level, int)
    if first:
        recursion_level = 0

        # TODO preprocess keys here so its not being done in every recursive call
        keys = listify(keys)

    found = []
    if isinstance(recursion_max, int) and recursion_level >= recursion_max:
        return found

    recursion_level += 1

    for arg in args:
        # TODO: Make this a callable
        # callback_dict: t.Optional[t.Callable] = None,
        """
        like:
        arg = callback_dict(arg)


        """
        if handle_dict and isinstance(arg, dict):
            arg = extract_key_values(arg, keys=keys)

        if isinstance(arg, (list, tuple, set, types.GeneratorType)):
            found.extend(
                # TODO ENSURE ALL ARGS ARE BEING PASSED TO RECURSIVE CALLS
                extract_strs(
                    *arg,
                    recursion_level=recursion_level,
                    recursion_max=recursion_max,
                    split=split,
                    keys=keys,
                    **kwargs,
                )
            )
            continue

        #
        if split and hasattr(arg, "splitlines"):
            found.extend(
                # TODO ENSURE ALL ARGS ARE BEING PASSED TO RECURSIVE CALLS
                extract_strs(
                    *arg.splitlines(),
                    recursion_level=recursion_level,
                    recursion_max=recursion_max,
                    split=False,
                    keys=keys,
                    **kwargs,
                )
            )

        # TODO: add support for skip_lines = str | t.Pattern
        arg_str = to_str(arg, **kwargs)

        # TODO: expected_type support
        # TODO: allow_empty support

        if isinstance(arg_str, str) and arg_str:
            found.append(arg_str)

    return found


# TODO: add support for csv
# TODO: add support for json
# TODO: add support for jsonl
"""
first hint: its a pathlib.Path
second hint: the string has one of the following extensions: .csv, .json, .jsonl
if isinstance(arg, str) and arg:
    check_path = pathlib.Path(arg)
    if check_path.is_file():
        arg = check_path

if isinstance(arg, pathlib.Path):
    if not arg.is_file():
        continue
    if arg.suffix not in [".csv", ".json", ".jsonl"]:
        continue
    if arg.suffix == ".csv":
        with arg.open("r") as fh:
            found.extend(
                extract_strs(
                    *fh.read(),
                    recursion_level=recursion_level + 1,
                    recursion_max=recursion_max,
                    split=False,
                    keys=keys,
                    **kwargs,
                )
            )
        continue
    if arg.suffix in [".json", ".jsonl"]:
        with arg.open("r") as fh:
            found.extend(
                extract_strs(
                    *fh.read(),
                    recursion_level=recursion_level + 1,
                    recursion_max=recursion_max,
                    split=False,
                    keys=keys,
                    **kwargs,
                )
            )
        continue


"""


def get_internal_axon_ids(
    *values: t.Any, keys: t.Sequence[str] = AXID.KEYS, **kwargs
) -> t.List[str]:
    """Extract internal_axon_ids from a set of values.

    Args:
        *values: values to extract from
        keys: keys to extract from if `values` is a dict
        **kwargs: passed to :meth:`extract_strs` and :meth:`get_internal_axon_id`

    Returns:
        list: list of internal_axon_ids found
    """
    return extract_strs(*values, callback=get_internal_axon_id, keys=keys, **kwargs)


# noinspection PyUnusedLocal
def get_internal_axon_id(
    value: t.Any = None,
    clean: bool = False,
    clean_keep: t.Sequence[str] = AXID.chars,
    check_length: t.Optional[int] = AXID.length,
    check_alphanumeric: bool = True,
    **kwargs,
) -> t.Optional[str]:
    """Extract an internal_axon_id from a string if possible.

    Args:
        value: value to extract from
        clean: True=clean characters not in `clean_keep` from `value` before `check_length` and
            `check_alphanumeric`
        clean_keep: characters to keep in `value` if `clean` is True
        check_length: length to check `value` against
        check_alphanumeric: True=check that `value` is alphanumeric
        **kwargs: unused

    Returns:
        str: internal_axon_id if found, None otherwise
    """
    if not isinstance(value, (str, bytes)):
        return None

    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")

    value = value.strip()

    if clean and clean_keep:
        value = "".join(x for x in value if x in clean_keep)

    return (
        None
        if not value
        or (isinstance(check_length, int) and not len(value) == check_length)
        or (check_alphanumeric and not value.isalnum())
        else value
    )


def join_and_or_not(
    *args: t.Union[str, bytes, t.Sequence[t.Union[str, bytes]]],
    and_flag: bool = False,
    not_flag: bool = False,
    wrap_flag: bool = False,
    str_and: str = " and ",
    str_or: str = " or ",
    str_not: str = "not ",
) -> str:
    """Build AQL for and/or/not of a set of queries.

    Args:
        *args: queries to join
        and_flag: True=join `queries` with " and ", False=join `queries` with " or "
        not_flag: prepend " not " to the joined `queries`
        wrap_flag: wrap the joined `queries` in parentheses
        str_and: string to join `queries` with if `and_flag` is True
        str_or: string to join `queries` with if `and_flag` is False
        str_not: string to prepend to the joined `queries` if `not_flag` is True
    """
    queries: t.List[str] = extract_strs(*args)
    if len(queries) > 1:
        queries = [f"({x})" for x in queries]
    joiner: str = str_and if and_flag else str_or
    query: str = joiner.join(queries)
    if query:
        if not_flag:
            query = f"{str_not} ({query})"
        if wrap_flag:
            query = f"({query})"
    return query
