"""Test suite for axonius_api_client.tools."""
import pytest
import datetime
from axonius_api_client.parsers.delta import (
    DateDeltaParser,
    get_tz,
    bytes_to_str,
    re_escape,
    re_join,
    is_empty,
    should_return_none,
    random_float,
    as_timezone,
    parse_datetime,
)
import dateutil.tz


class TestRandomFloat:
    @pytest.mark.parametrize(
        "min_value,max_value,places",
        [
            (1, 10, 2),
            (-5, 5, 3),
            (0, 100, 0),
            (0.1, 0.9, 4),
        ],
    )
    def test_random_float_range(self, min_value, max_value, places):
        result = random_float(min_value, max_value, places)
        assert isinstance(result, float)
        assert min_value <= result <= max_value
        decimal_places = len(str(result).split(".")[1]) if "." in str(result) and places > 0 else 0
        assert decimal_places <= places

    def test_random_float_repeatability(self):
        results = [random_float(1, 10, 2) for _ in range(100)]
        assert len(set(results)) > 1


class TestShouldReturnNone:
    @pytest.mark.parametrize(
        "input_value,allow_none,allow_empty,empty,expected",
        [
            (None, False, False, None, False),
            (None, True, False, None, True),
            ("", False, False, None, False),
            ("", False, True, None, True),
            ("  ", False, True, None, True),
            ("none", False, True, None, True),
            ("not empty", False, True, None, False),
            (None, True, True, None, True),
            (None, True, True, ("", "null", "none", None), True),
            ("", True, True, ("", "null", "none", None), True),
            ("  ", True, True, ("", "null", "none", None), True),
            ("none", True, True, ("", "null", "none", None), True),
            ("not empty", True, True, ("", "null", "none", None), False),
        ],
    )
    def test_should_return_none(self, input_value, allow_none, allow_empty, empty, expected):
        if empty is None:
            result = should_return_none(input_value, allow_none, allow_empty)
        else:
            result = should_return_none(input_value, allow_none, allow_empty, empty)
        assert result == expected


class TestBytesToStr:
    @pytest.mark.parametrize(
        "input_value,encoding,errors,expected",
        [
            (b"Hello, World!", "utf-8", "strict", "Hello, World!"),
            (b"Hello, World!\x80", "utf-8", "ignore", "Hello, World!"),
            (b"Hello, World!\x80", "utf-8", "replace", "Hello, World!�"),
            ("Hello, World!", "utf-8", "strict", "Hello, World!"),
            (42, "utf-8", "strict", 42),
        ],
    )
    def test_bytes_to_str(self, input_value, encoding, errors, expected):
        result = bytes_to_str(input_value, encoding, errors)
        assert result == expected


class TestIsEmpty:
    @pytest.mark.parametrize(
        "input_value,empty,expected",
        [
            ("", None, True),
            ("  ", None, True),
            ("null", None, True),
            ("none", None, True),
            ("not empty", None, False),
            (None, None, True),
            ("", ("", "null", "none", None), True),
            ("  ", ("", "null", "none", None), True),
            ("null", ("", "null", "none", None), True),
            ("none", ("", "null", "none", None), True),
            ("not empty", ("", "null", "none", None), False),
            (None, ("", "null", "none", None), True),
        ],
    )
    def test_is_empty(self, input_value, empty, expected):
        if empty is None:
            result = is_empty(input_value)
        else:
            result = is_empty(input_value, empty)
        assert result == expected


class TestReEscape:
    @pytest.mark.parametrize(
        "input_value,expected",
        [
            ("example", r"example"),
            ("[1, 2]", r"\[1,\ 2\]"),
            ("(a+b)", r"\(a\+b\)"),
            ("https://example.com", r"https://example\.com"),
            (b"hello", r"hello"),
        ],
    )
    def test_re_escape(self, input_value, expected):
        result = re_escape(input_value)
        assert result == expected


class TestReJoin:
    @pytest.mark.parametrize(
        "input_args,expected",
        [
            (("example", "test"), r"example|test"),
            (("abc", "123"), r"abc|123"),
            (("[a-z]", "[0-9]"), r"\[a\-z\]|\[0\-9\]"),
            (("hello", "world"), r"hello|world"),
        ],
    )
    def test_re_join(self, input_args, expected):
        result = re_join(*input_args)
        assert result == expected


class TestDateDeltaParser:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("now", {"is_match": False, "datetime": None, "marker": None, "delta": None}),
            ("now~", {"is_match": True, "datetime": "now", "marker": "~", "delta": ""}),
            ("now~1", {"is_match": True, "datetime": "now", "marker": "~", "delta": "1"}),
            ("now~1d", {"is_match": True, "datetime": "now", "marker": "~", "delta": "1d"}),
            (
                "now~1d2h3m4s5ms6us",
                {"is_match": True, "datetime": "now", "marker": "~", "delta": "1d2h3m4s5ms6us"},
            ),
            ("Feb 1, 2020", {"is_match": False, "datetime": None, "marker": None, "delta": None}),
            ("~", {"is_match": True, "datetime": "", "marker": "~", "delta": ""}),
            ("~ 1d", {"is_match": True, "datetime": "", "marker": "~", "delta": " 1d"}),
            ("", {"is_match": False, "datetime": None, "marker": None, "delta": None}),
        ],
    )
    def test_datetime_delta(self, value, expected):
        dt_delta = DateDeltaParser(value)
        assert dt_delta.is_match == expected["is_match"]
        assert dt_delta.match_datetime == expected["datetime"]
        assert dt_delta.match_marker == expected["marker"]
        assert dt_delta.match_delta == expected["delta"]


class TestGetTz:
    @pytest.mark.parametrize(
        "input_tz",
        [
            "Invalid/Timezone",
            "Wrong_Timezone",
        ],
    )
    def test_invalid_tz(self, input_tz):
        with pytest.raises(ValueError):
            get_tz(input_tz)

    @pytest.mark.parametrize(
        "input_tz,expected",
        [
            ("Invalid/Timezone", "non_error"),
            ("Another/InvalidZone", "non_error"),
        ],
    )
    def test_invalid_tz_no_error_return_non_error(self, input_tz, expected):
        result = get_tz(input_tz, error_raise=False, as_none=expected)
        assert result == expected

    @pytest.mark.parametrize(
        "input_tz",
        [
            None,
            "",
            "  ",
        ],
    )
    def test_none_empty_tz(self, input_tz):
        result = get_tz(input_tz, error_raise=False, allow_none=True, allow_empty=True)
        assert result is None

    def test_error_on_empty(self):
        with pytest.raises(ValueError):
            get_tz("", error_raise=True, allow_none=False, allow_empty=False)

    @pytest.mark.parametrize(
        "input_tz,expected",
        [
            ("UTC", datetime.timezone.utc),
            ("America/New_York", dateutil.tz.gettz("America/New_York")),
            ("Asia/Kolkata", dateutil.tz.gettz("Asia/Kolkata")),
            (datetime.timezone.utc, datetime.timezone.utc),
            ("Europe/Berlin", dateutil.tz.gettz("Europe/Berlin")),
        ],
    )
    def test_valid_tz(self, input_tz, expected):
        result = get_tz(input_tz)
        assert result.utcoffset(datetime.datetime.utcnow()) == expected.utcoffset(
            datetime.datetime.utcnow()
        )

    def test_error_on_none(self):
        with pytest.raises(TypeError):
            get_tz(None, error_raise=True, allow_none=False)


class TestAsTimezone:
    @pytest.mark.parametrize(
        "input_datetime, input_tz, expected",
        [
            (
                datetime.datetime(2023, 4, 6, 12, 0, tzinfo=datetime.timezone.utc),
                "America/New_York",
                datetime.datetime(2023, 4, 6, 8, 0, tzinfo=dateutil.tz.gettz("America/New_York")),
            ),
            (
                datetime.datetime(2023, 4, 6, 12, 0, tzinfo=datetime.timezone.utc),
                "Asia/Kolkata",
                datetime.datetime(2023, 4, 6, 17, 30, tzinfo=dateutil.tz.gettz("Asia/Kolkata")),
            ),
            (
                datetime.datetime(2023, 4, 6, 12, 0, tzinfo=dateutil.tz.gettz("Asia/Kolkata")),
                "UTC",
                datetime.datetime(2023, 4, 6, 6, 30, tzinfo=datetime.timezone.utc),
            ),
        ],
    )
    def test_valid_timezone_conversion(self, input_datetime, input_tz, expected):
        result = as_timezone(value=input_datetime, tz=input_tz)
        assert result == expected

    def test_invalid_timezone_error(self):
        dt = datetime.datetime(2023, 4, 6, 12, 0, tzinfo=datetime.timezone.utc)
        invalid_tz = "Invalid/Timezone"
        with pytest.raises(ValueError):
            as_timezone(value=dt, tz=invalid_tz)

    def test_allow_none(self):
        dt = datetime.datetime(2023, 4, 6, 12, 0, tzinfo=datetime.timezone.utc)
        result = as_timezone(value=dt, tz=None, allow_none=True)
        assert result == dt

    def test_allow_empty(self):
        dt = datetime.datetime(2023, 4, 6, 12, 0, tzinfo=datetime.timezone.utc)
        result = as_timezone(value=dt, tz="", allow_empty=True)
        assert result == dt

    def test_as_none(self):
        dt = datetime.datetime(2023, 4, 6, 12, 0, tzinfo=datetime.timezone.utc)
        result = as_timezone(
            value=dt, tz="Invalid/Timezone", error_raise=False, as_none="non_error"
        )
        assert result == dt


def get_approximate_datetime(seconds=1):
    """

    Args:
        seconds:

    Returns:

    """
    return (datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)).astimezone(
        datetime.timezone.utc
    )


class TestParseDatetime:
    @pytest.mark.parametrize(
        "input_value,expected",
        [
            (
                "2023-04-06T12:00:00Z",
                datetime.datetime(2023, 4, 6, 12, 0, 0).astimezone(datetime.timezone.utc),
            ),
            (
                "2023-04-06 12:00:00",
                datetime.datetime(
                    2023,
                    4,
                    6,
                    12,
                    0,
                    0,
                ).astimezone(datetime.timezone.utc),
            ),
            ("now", datetime.datetime.utcnow().astimezone(datetime.timezone.utc)),
            ("today", datetime.datetime.utcnow().astimezone(datetime.timezone.utc)),
            ("current", datetime.datetime.utcnow().astimezone(datetime.timezone.utc)),
            (
                datetime.datetime(2023, 4, 6, 12, 0, 0, tzinfo=dateutil.tz.gettz()),
                datetime.datetime(2023, 4, 6, 12, 0, 0).astimezone(datetime.timezone.utc),
            ),
        ],
    )
    def test_valid_datetime(self, input_value, expected):
        result = parse_datetime(input_value)
        delta = result - expected
        assert delta < datetime.timedelta(seconds=15)

    @pytest.mark.parametrize("invalid_value", ["invalid_datetime", "not a date"])
    def test_invalid_datetime(self, invalid_value):
        with pytest.raises(ValueError):
            parse_datetime(invalid_value)

    def test_allow_none(self):
        assert parse_datetime(None, allow_none=True) is None

    def test_allow_empty(self):
        assert parse_datetime("", allow_empty=True) is None

    def test_allow_none_false(self):
        with pytest.raises(TypeError):
            parse_datetime(None, allow_none=False)
