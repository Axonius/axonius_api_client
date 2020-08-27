# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client."""
import tempfile

import pytest

from axonius_api_client.exceptions import ToolsError
from axonius_api_client.tools import (
    coerce_bool,
    coerce_int,
    datetime,
    dt_min_ago,
    dt_now,
    dt_parse,
    dt_within_min,
    get_path,
    grouper,
    is_int,
    join_url,
    json_dump,
    json_load,
    json_reload,
    listify,
    path_read,
    path_write,
    pathlib,
    strip_left,
    strip_right,
    timedelta,
)

from ..utils import IS_WINDOWS

'''
class TestValType:
    """Test axonius_api_client.val_type."""

    def test_good(self):
        """Pass."""
        val_type(1, INT)

    def test_bad(self):
        """Pass."""
        with pytest.raises(ToolsError):
            val_type("", INT)
'''


class TestCoerce:
    """Test axonius_api_client.join_url."""

    def test_int(self):
        """Pass."""
        with pytest.raises(ToolsError):
            coerce_int("badwolf")

        assert coerce_int("456") == 456

    def test_bool(self):
        """Pass."""
        with pytest.raises(ToolsError):
            coerce_bool("badwolf")

        assert coerce_bool("y") is True
        assert coerce_bool("yes") is True
        assert coerce_bool("true") is True
        assert coerce_bool("True") is True
        assert coerce_bool("1") is True
        assert coerce_bool(1) is True
        assert coerce_bool("t") is True
        assert coerce_bool(True) is True
        assert coerce_bool("n") is False
        assert coerce_bool("no") is False
        assert coerce_bool("false") is False
        assert coerce_bool("False") is False
        assert coerce_bool("0") is False
        assert coerce_bool(0) is False
        assert coerce_bool("f") is False
        assert coerce_bool(False) is False


class TestJoinUrl:
    """Test axonius_api_client.join_url."""

    def test_url(self):
        """Test url gets joined properly no matter the slashes."""
        r = join_url("https://test.com")
        assert r == "https://test.com/"
        r = join_url("https://test.com/")
        assert r == "https://test.com/"
        r = join_url("https://test.com////")
        assert r == "https://test.com/"
        r = join_url("https://test.com", "")
        assert r == "https://test.com/"
        r = join_url("https://test.com", "", "")
        assert r == "https://test.com/"
        r = join_url("https://test.com", "/", "")
        assert r == "https://test.com/"
        r = join_url("https://test.com", "/", "/")
        assert r == "https://test.com/"

    def test_url_path(self):
        """Test url, path gets joined properly no matter the slashes."""
        r = join_url("https://test.com", "a")
        assert r == "https://test.com/a"
        r = join_url("https://test.com", "/a")
        assert r == "https://test.com/a"
        r = join_url("https://test.com", "//a")
        assert r == "https://test.com/a"
        r = join_url("https://test.com", "a/")
        assert r == "https://test.com/a/"
        r = join_url("https://test.com", "a/b")
        assert r == "https://test.com/a/b"
        r = join_url("https://test.com", "a/b", "")
        assert r == "https://test.com/a/b"
        r = join_url("https://test.com", "a/b/", "")
        assert r == "https://test.com/a/b/"
        r = join_url("https://test.com", "a/b", "/")
        assert r == "https://test.com/a/b/"
        r = join_url("https://test.com", "a/b", "/////")
        assert r == "https://test.com/a/b/"

    def test_url_path_route(self):
        """Test url, path, route gets joined properly no matter the slashes."""
        r = join_url("https://test.com", "a", "b")
        assert r == "https://test.com/a/b"
        r = join_url("https://test.com", "/a", "b")
        assert r == "https://test.com/a/b"
        r = join_url("https://test.com", "//a", "b")
        assert r == "https://test.com/a/b"
        r = join_url("https://test.com", "a", "b/c/d")
        assert r == "https://test.com/a/b/c/d"


'''
class TestJoinDot:
    """Test axonius_api_client.join_dot."""

    def test_multi(self):
        """Test dot join multi."""
        r = join_dot(obj=["x", "a", "c"])
        assert r == "x.a.c"

    def test_multi_with_empty_false(self):
        """Test dot join multi with empty=False."""
        r = join_dot(obj=["x", "", "a", None, "c", []], empty=False)
        assert r == "x.a.c"

    def test_multi_with_empty_true(self):
        """Test dot join multi with empty=True."""
        r = join_dot(obj=["x", "", "a", None, "c"], empty=True)
        assert r == "x..a.None.c"

    def test_single(self):
        """Test dot join single."""
        r = join_dot(obj=["x"])
        assert r == "x"

    def test_non_list(self):
        """Test dot join single."""
        r = join_dot(obj="x")
        assert r == "x"

    def test_empty_list(self):
        """Test dot join single."""
        r = join_dot(obj=[])
        assert r == ""

    def test_single_none(self):
        """Test dot join with None."""
        r = join_dot(obj=None)
        assert r == ""


class TestJoinComma:
    """Test axonius_api_client.join_dot."""

    def test_multi(self):
        """Test comma join multi."""
        r = join_comma(obj=["x", "a", "c"])
        assert r == "x, a, c"

    def test_multi_no_indent(self):
        """Test comma join multi with indent=False."""
        r = join_comma(obj=["x", "a", "c"], indent=False)
        assert r == "x,a,c"

    def test_multi_with_empty_false(self):
        """Test comma join multi with empty=False."""
        r = join_comma(obj=["x", "", "a", None, "c", []], empty=False)
        assert r == "x, a, c"

    def test_multi_with_empty_true(self):
        """Test comma join list with multi items with empty=True."""
        r = join_comma(obj=["x", "", "a", None, "c"], empty=True)
        assert r == "x, , a, None, c"

    def test_single(self):
        """Test comma join list with single item."""
        r = join_comma(obj=["x"])
        assert r == "x"

    def test_non_list(self):
        """Test comma non list."""
        r = join_comma(obj="x")
        assert r == "x"

    def test_empty_list(self):
        """Test comma empty list."""
        r = join_comma(obj=[])
        assert r == ""

    def test_single_none(self):
        """Test comma join with None."""
        r = join_comma(obj=None)
        assert r == ""


class TestJoinCr:
    """Test axonius_api_client.join_cr."""

    def test_multi(self):
        """Test cr join multi."""
        r = join_cr(obj=["x", "a", "c"])
        assert r == "\n  x\n  a\n  c"

    def test_single(self):
        """Test cr join multi."""
        r = join_cr(obj=["x"])
        assert r == "\n  x"

    def test_single_non_list(self):
        """Test cr join list w/ single entry."""
        r = join_cr(obj="x")
        assert r == "\n  x"

    def test_single_empty_list(self):
        """Test cr join empty list."""
        r = join_cr(obj=[])
        assert r == ""

    def test_single_none(self):
        """Test cr join with None."""
        r = join_cr(obj=None)
        assert r == ""

    def test_post_and_pre(self):
        """Test cr join with post and pre = True."""
        r = join_cr(obj=["x", "a", "c"], pre=True, post=True)
        assert r == "\n  x\n  a\n  c\n  "
'''


class TestGetPath:
    """Test axonius_api_client.get_path."""

    def test_str(self):
        """Test resolve with a string."""
        r = get_path(obj="/../badwolf")
        assert isinstance(r, pathlib.Path)
        if IS_WINDOWS:
            assert format(r).endswith("badwolf")
        else:
            assert format(r) == format("/badwolf")

    def test_pathlib(self):
        """Test resolve with a pathlib.Path."""
        r = get_path(obj=pathlib.Path("."))
        assert isinstance(r, pathlib.Path)

    def test_user(self):
        """Test resolve with ~."""
        r = get_path(obj="~")
        assert isinstance(r, pathlib.Path)
        assert format(r) == format(pathlib.Path.home())


class TestPathWrite:
    """Test axonius_api_client.path_write."""

    def test_simple_pathlib(self, tmp_path):
        """Test simple write with pathlib object."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = path_write(obj=path, data=data)
        assert ret_path.read_text() == data
        assert format(ret_path) == format(path)
        assert ret_write == len(data)
        if IS_WINDOWS:
            assert ret_path.stat().st_mode == 33206
            assert ret_path.parent.stat().st_mode == 16895
        else:
            assert ret_path.stat().st_mode == 33152
            assert ret_path.parent.stat().st_mode == 16832

    def test_simple_str(self, tmp_path):
        """Test simple write with path as str."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = path_write(obj=format(path), data=data)
        assert ret_path.read_text() == data
        assert format(ret_path) == format(path)
        assert ret_write == len(data)

    def test_parent_fail(self, tmp_path):
        """Test simple write with pathlib object."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        with pytest.raises(ToolsError):
            path_write(obj=path, data=data, make_parent=False)

    def test_noperm_parent(self):
        """Pass."""
        tmpdir = pathlib.Path(tempfile.gettempdir())
        path = tmpdir / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = path_write(obj=path, data=data, overwrite=True)
        assert ret_path.read_text() == data

    def test_overwrite_false(self, tmp_path):
        """Test overwrite=False."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        path_write(obj=path, data=data)
        with pytest.raises(ToolsError):
            path_write(obj=path, data=data, overwrite=False)

    def test_overwrite_true(self, tmp_path):
        """Test overwrite=True."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        path_write(obj=path, data=data)
        path_write(obj=path, data=data, overwrite=True)
        assert path.is_file()

    def test_binary_true_nonbinary(self, tmp_path):
        """Test binary=True with nonbinary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = path_write(obj=path, data=data, binary=True)
        assert ret_path.read_text() == "abc\n123\n"
        if IS_WINDOWS:
            assert ret_path.read_bytes() == b"abc\n123\n"
        else:
            assert ret_path.read_bytes() == b"abc\n123\n"

    def test_binary_true_binary(self, tmp_path):
        """Test binary=True with binary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = b"abc\n123\n"
        ret_path, ret_write = path_write(obj=path, data=data, binary=True)
        assert ret_path.read_text() == "abc\n123\n"
        if IS_WINDOWS:
            assert ret_path.read_bytes() == b"abc\n123\n"
        else:
            assert ret_path.read_bytes() == b"abc\n123\n"

    def test_binary_false_nonbinary(self, tmp_path):
        """Test binary=False with nonbinary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = path_write(obj=path, data=data, binary=False)
        assert ret_path.read_text() == "abc\n123\n"
        if IS_WINDOWS:
            assert ret_path.read_bytes() == b"abc\r\n123\r\n"
        else:
            assert ret_path.read_bytes() == b"abc\n123\n"

    def test_binary_false_binary(self, tmp_path):
        """Test binary=False with binary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = b"abc\n123\n"
        ret_path, ret_write = path_write(obj=path, data=data, binary=False)
        assert ret_path.read_text() == "abc\n123\n"
        if IS_WINDOWS:
            assert ret_path.read_bytes() == b"abc\r\n123\r\n"
        else:
            assert ret_path.read_bytes() == b"abc\n123\n"

    def test_is_json_false_dotjson_nonjson(self, tmp_path):
        """Test is_json=False with .json in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = b""
        ret_path, ret_write = path_write(obj=path, data=data, is_json=False)
        assert ret_path.read_text() == data.decode()

    def test_is_json_false_dotjson_json(self, tmp_path):
        """Test is_json=False with .json in filename and valid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = {"x": 2}
        ret_path, ret_write = path_write(obj=path, data=data, is_json=False)
        assert ret_path.read_text() == '{\n  "x": 2\n}'

    def test_is_json_true_nonjson(self, tmp_path):
        """Test is_json=True with .json not in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.text"
        data = pytest
        with pytest.raises(Exception):
            path_write(obj=path, data=data, is_json=True)

    def test_is_json_true_json(self, tmp_path):
        """Test is_json=True with .json not in filename and valid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.text"
        data = {"x": 2}
        ret_path, ret_write = path_write(obj=path, data=data, is_json=True)
        assert ret_path.read_text() == '{\n  "x": 2\n}'


class TestPathRead:
    """Test axonius_api_client.path_read."""

    def test_pathlib(self, tmp_path):
        """Test simple write with pathlib object."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = path_write(obj=path, data=data)
        rret_path, ret_read = path_read(obj=path)
        assert wret_path == rret_path
        assert ret_read == data

    def test_str(self, tmp_path):
        """Test simple write with str."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = path_write(obj=path, data=data)
        rret_path, ret_read = path_read(obj=format(path))
        assert wret_path == rret_path
        assert ret_read == data

    def test_binary_true(self, tmp_path):
        """Test binary=True."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = path_write(obj=path, data=data)
        rret_path, ret_read = path_read(obj=format(path), binary=True)
        assert wret_path == rret_path
        if IS_WINDOWS:
            assert ret_read == b"abc\r\n123\r\n"
        else:
            assert ret_read == b"abc\n123\n"

    def test_binary_false(self, tmp_path):
        """Test binary=False."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = path_write(obj=path, data=data)
        rret_path, ret_read = path_read(obj=format(path), binary=False)
        assert wret_path == rret_path
        assert ret_read == data

    def test_is_json_true_nonjson(self, tmp_path):
        """Test is_json=True with .json not in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.text"
        data = "abc\n123\n"
        wret_path, ret_write = path_write(obj=path, data=data)
        with pytest.raises(Exception):
            path_read(obj=path, is_json=True)

    def test_is_json_false_dotjson_nonjson(self, tmp_path):
        """Test is_json=False with .json in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = "abc\n123\n"
        wret_path, ret_write = path_write(obj=path, data=data)
        rret_path, ret_read = path_read(obj=path, is_json=False)
        assert wret_path == rret_path
        assert ret_read == data

    def test_is_json_false_dotjson_json(self, tmp_path):
        """Test is_json=False with .json in filename and valid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = {"x": 2}
        wret_path, ret_write = path_write(obj=path, data=data)
        rret_path, ret_read = path_read(obj=path, is_json=False)
        assert wret_path == rret_path
        assert ret_read == data

    def test_not_found(self, tmp_path):
        """Test is_json=False with .json in filename and valid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        with pytest.raises(ToolsError):
            path_read(obj=path)


class TestGrouper:
    """Test grouper."""

    def test_iter(self):
        """Simple test."""
        x = list(grouper([1, 2, 3, 4, 5, 6], 2))
        assert x == [(1, 2), (3, 4), (5, 6)]

    def test_iter_off1(self):
        """Simple test."""
        x = list(grouper([1, 2, 3, 4, 5, 6, 7], 2))
        assert x == [(1, 2), (3, 4), (5, 6), (7, None)]

    def test_iter_off1_strfill(self):
        """Simple test."""
        x = list(grouper([1, 2, 3, 4, 5, 6, 7], 2, "x"))
        assert x == [(1, 2), (3, 4), (5, 6), (7, "x")]


'''
class TestNestDepth:
    """Test listify."""

    def test_dict1(self):
        """Simple test."""
        x = nest_depth(obj={"x": 1, "y": 1})
        assert x == 1

    def test_dict2(self):
        """Simple test."""
        x = nest_depth(obj={"x": 1, "y": {"z": 1}})
        assert x == 2

    def test_tuple(self):
        """Simple test."""
        x = nest_depth(obj=(1, 2))
        assert x == 1

    def test_list1(self):
        """Simple test."""
        x = nest_depth(obj=[1, 2])
        assert x == 1

    def test_list2(self):
        """Simple test."""
        x = nest_depth(obj=[[1], [2]])
        assert x == 2

    @pytest.mark.parametrize("val", [1, "1", None], scope="class")
    def test_not_complex(self, val):
        """Simple test."""
        x = nest_depth(obj=val)
        assert x == 0

    def test_mix(self):
        """Simple test."""
        x = nest_depth(obj=["1", ["a", {}]])
        assert x == 3

'''


class TestListify:
    """Test listify."""

    def test_dict_keys(self):
        """Simple test."""
        x = listify(obj={"x": 1, "y": 1}, dictkeys=True)
        assert x == ["x", "y"]

    def test_dict_notkeys(self):
        """Simple test."""
        x = listify(obj={"x": 1, "y": 1}, dictkeys=False)
        assert x == [{"x": 1, "y": 1}]

    def test_tuple(self):
        """Simple test."""
        x = listify(obj=(1, 2))
        assert x == [1, 2]

    def test_list(self):
        """Simple test."""
        x = listify(obj=[1, 2])
        assert x == [1, 2]

    def test_int(self):
        """Simple test."""
        x = listify(obj=1)
        assert x == [1]

    def test_str(self):
        """Simple test."""
        x = listify(obj="1")
        assert x == ["1"]

    def test_none(self):
        """Simple test."""
        x = listify(obj=None)
        assert x == []


class TestIsInt:
    """Test is_*."""

    @pytest.mark.parametrize("ok", [0, 4], scope="class")
    @pytest.mark.parametrize("bad", ["1", False, True, b"1"], scope="class")
    def test_int_digit_false(self, ok, bad):
        """Simple test."""
        assert is_int(obj=ok, digit=False)
        assert not is_int(obj=bad, digit=False)

    @pytest.mark.parametrize("ok", [0, 4, "1", b"1"], scope="class")
    @pytest.mark.parametrize("bad", [False, True, {}, "x", b"x"], scope="class")
    def test_int_digit_true(self, ok, bad):
        """Simple test."""
        assert is_int(obj=ok, digit=True)
        assert not is_int(obj=bad, digit=True)


class TestStripLeft:
    """Test strip_left."""

    def test_left_str(self):
        """Simple test."""
        x = "badwolfbadwolf"
        y = strip_left(obj=x, fix="badwolf")
        assert y == "badwolf"

    def test_left_list(self):
        """Simple test."""
        x = ["badwolfbadwolf", "badwolf", "abadwolfbadwolf"]
        y = strip_left(obj=x, fix="badwolf")
        assert y == ["badwolf", "", "abadwolfbadwolf"]

    def test_left_str_nomatch(self):
        """Simple test."""
        x = "abadwolfbadwolf"
        y = strip_left(obj=x, fix="badwolf")
        assert y == "abadwolfbadwolf"


class TestStripRight:
    """Test strip_right."""

    def test_right_str(self):
        """Simple test."""
        x = "badwolfbadwolf"
        y = strip_right(obj=x, fix="badwolf")
        assert y == "badwolf"

    def test_right_str_nomatch(self):
        """Simple test."""
        x = "badwolfbadwolfa"
        y = strip_right(obj=x, fix="badwolf")
        assert y == "badwolfbadwolfa"

    def test_right_list(self):
        """Simple test."""
        x = ["badwolfbadwolf", "badwolf", "badwolfbadwolfa"]
        y = strip_right(obj=x, fix="badwolf")
        assert y == ["badwolf", "", "badwolfbadwolfa"]


class TestJsonLoad:
    """Test json_load."""

    def test_load(self):
        """Simple test."""
        x = "{}"
        y = json_load(obj=x)
        assert y == {}

    def test_load_error_false(self):
        """Simple test."""
        x = "xxx"
        y = json_load(obj=x, error=False)
        assert y == "xxx"

    def test_load_error_true(self):
        """Simple test."""
        x = "xxx"
        with pytest.raises(Exception):
            json_load(obj=x, error=True)


class TestJsonDump:
    """Test json_dump."""

    def test_dump(self):
        """Simple test."""
        x = {"x": 2}
        y = json_dump(obj=x)
        assert y == '{\n  "x": 2\n}'

    def test_dump_error_false(self):
        """Simple test."""
        x = pytest
        y = json_dump(obj=x, error=False)
        assert y == pytest

    def test_dump_error_true(self):
        """Simple test."""
        x = pytest
        with pytest.raises(Exception):
            json_dump(obj=x, error=True)


class TestJsonReload:
    """Test json_dump."""

    def test_re_load(self):
        """Simple test."""
        x = '{"x": 2}'
        y = json_reload(obj=x)
        assert y == '{\n  "x": 2\n}'

    def test_re_load_error_false(self):
        """Simple test."""
        x = "{"
        y = json_reload(obj=x, error=False)
        assert y == x

    def test_re_load_error_true(self):
        """Simple test."""
        x = "{"
        with pytest.raises(Exception):
            json_reload(obj=x, error=True)


class TestDtMinAgo:
    """Test dt_*."""

    def test_min_ago_utc_str(self):
        """Simple test."""
        then = format(dt_now() - timedelta(minutes=1))
        assert dt_min_ago(obj=then) == 1

    def test_min_ago_utc_dt(self):
        """Simple test."""
        then = dt_now() - timedelta(minutes=1)
        assert dt_min_ago(obj=then) == 1

    def test_min_ago_utc_dt_naive(self):
        """Simple test."""
        then = dt_now(None) - timedelta(minutes=1)
        assert dt_min_ago(obj=then) == 1

    def test_min_ago_utc_dtdelta(self):
        """Simple test."""
        then = timedelta(minutes=3)
        assert dt_min_ago(obj=then) == 3

    def test_min_ago_naive(self):
        """Simple test."""
        then = datetime.now() - timedelta(minutes=1)
        assert dt_min_ago(obj=format(then)) == 1


class TestDtNow:
    """Test dt_*."""

    def test_now(self):
        """Pass."""
        now = dt_now()
        assert now.tzinfo

    def test_now_notz(self):
        """Pass."""
        now = dt_now(tz=None)
        assert not now.tzinfo

    def test_now_delta(self):
        """Pass."""
        then = dt_now(delta=timedelta(minutes=5))
        assert dt_min_ago(then) == 5


class TestDtParse:
    """Test dt_*."""

    @pytest.mark.parametrize(
        "val", [format(dt_now()), dt_now(), timedelta(minutes=1)], scope="class",
    )
    def test_val(self, val):
        """Pass."""
        now = dt_parse(obj=val)
        assert isinstance(now, datetime)

    def test_list(self):
        """Pass."""
        now = [format(dt_now())]
        now = dt_parse(obj=now)
        assert isinstance(now, list)
        assert [isinstance(x, datetime) for x in now]


class TestDtWithinMin:
    """Test dt_*."""

    @pytest.mark.parametrize(
        "val", [None, "x", False, True, {}, [], 6, "8", b"9"], scope="class"
    )
    def test_bad(self, val):
        """Pass."""
        then = dt_now(delta=timedelta(minutes=5))
        assert dt_within_min(obj=then, n=val) is False

    @pytest.mark.parametrize("val", [0, 4, "1", b"2"], scope="class")
    def test_ok(self, val):
        """Pass."""
        then = dt_now(delta=timedelta(minutes=5))
        assert dt_within_min(obj=then, n=val) is True
