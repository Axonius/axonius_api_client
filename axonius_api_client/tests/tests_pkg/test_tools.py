# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import tempfile

import pytest

from axonius_api_client import exceptions, tools


class TestCoerce(object):
    """Test axonius_api_client.tools.join_url."""

    def test_int(self):
        """Pass."""
        with pytest.raises(exceptions.ToolsError):
            tools.coerce_int("badwolf")

        assert tools.coerce_int("456") == 456

    def test_bool(self):
        """Pass."""
        with pytest.raises(exceptions.ToolsError):
            tools.coerce_bool("badwolf")

        assert tools.coerce_bool("y") is True
        assert tools.coerce_bool("yes") is True
        assert tools.coerce_bool("true") is True
        assert tools.coerce_bool("True") is True
        assert tools.coerce_bool("1") is True
        assert tools.coerce_bool(1) is True
        assert tools.coerce_bool("t") is True
        assert tools.coerce_bool(True) is True
        assert tools.coerce_bool("n") is False
        assert tools.coerce_bool("no") is False
        assert tools.coerce_bool("false") is False
        assert tools.coerce_bool("False") is False
        assert tools.coerce_bool("0") is False
        assert tools.coerce_bool(0) is False
        assert tools.coerce_bool("f") is False
        assert tools.coerce_bool(False) is False


class TestJoinUrl(object):
    """Test axonius_api_client.tools.join_url."""

    def test_url(self):
        """Test url gets joined properly no matter the slashes."""
        r = tools.join_url("https://test.com")
        assert r == "https://test.com/"
        r = tools.join_url("https://test.com/")
        assert r == "https://test.com/"
        r = tools.join_url("https://test.com////")
        assert r == "https://test.com/"
        r = tools.join_url("https://test.com", "")
        assert r == "https://test.com/"
        r = tools.join_url("https://test.com", "", "")
        assert r == "https://test.com/"
        r = tools.join_url("https://test.com", "/", "")
        assert r == "https://test.com/"
        r = tools.join_url("https://test.com", "/", "/")
        assert r == "https://test.com/"

    def test_url_path(self):
        """Test url, path gets joined properly no matter the slashes."""
        r = tools.join_url("https://test.com", "a")
        assert r == "https://test.com/a"
        r = tools.join_url("https://test.com", "/a")
        assert r == "https://test.com/a"
        r = tools.join_url("https://test.com", "//a")
        assert r == "https://test.com/a"
        r = tools.join_url("https://test.com", "a/")
        assert r == "https://test.com/a/"
        r = tools.join_url("https://test.com", "a/b")
        assert r == "https://test.com/a/b"
        r = tools.join_url("https://test.com", "a/b", "")
        assert r == "https://test.com/a/b"
        r = tools.join_url("https://test.com", "a/b/", "")
        assert r == "https://test.com/a/b/"
        r = tools.join_url("https://test.com", "a/b", "/")
        assert r == "https://test.com/a/b/"
        r = tools.join_url("https://test.com", "a/b", "/////")
        assert r == "https://test.com/a/b/"

    def test_url_path_route(self):
        """Test url, path, route gets joined properly no matter the slashes."""
        r = tools.join_url("https://test.com", "a", "b")
        assert r == "https://test.com/a/b"
        r = tools.join_url("https://test.com", "/a", "b")
        assert r == "https://test.com/a/b"
        r = tools.join_url("https://test.com", "//a", "b")
        assert r == "https://test.com/a/b"
        r = tools.join_url("https://test.com", "a", "b/c/d")
        assert r == "https://test.com/a/b/c/d"


class TestJoinDot(object):
    """Test axonius_api_client.tools.join_dot."""

    def test_multi(self):
        """Test dot join multi."""
        r = tools.join_dot(obj=["x", "a", "c"])
        assert r == "x.a.c"

    def test_multi_with_empty_false(self):
        """Test dot join multi with empty=False."""
        r = tools.join_dot(obj=["x", "", "a", None, "c", []], empty=False)
        assert r == "x.a.c"

    def test_multi_with_empty_true(self):
        """Test dot join multi with empty=True."""
        r = tools.join_dot(obj=["x", "", "a", None, "c"], empty=True)
        assert r == "x..a.None.c"

    def test_single(self):
        """Test dot join single."""
        r = tools.join_dot(obj=["x"])
        assert r == "x"

    def test_non_list(self):
        """Test dot join single."""
        r = tools.join_dot(obj="x")
        assert r == "x"

    def test_empty_list(self):
        """Test dot join single."""
        r = tools.join_dot(obj=[])
        assert r == ""

    def test_single_none(self):
        """Test dot join with None."""
        r = tools.join_dot(obj=None)
        assert r == ""


class TestJoinComma(object):
    """Test axonius_api_client.tools.join_dot."""

    def test_multi(self):
        """Test comma join multi."""
        r = tools.join_comma(obj=["x", "a", "c"])
        assert r == "x, a, c"

    def test_multi_no_indent(self):
        """Test comma join multi with indent=False."""
        r = tools.join_comma(obj=["x", "a", "c"], indent=False)
        assert r == "x,a,c"

    def test_multi_with_empty_false(self):
        """Test comma join multi with empty=False."""
        r = tools.join_comma(obj=["x", "", "a", None, "c", []], empty=False)
        assert r == "x, a, c"

    def test_multi_with_empty_true(self):
        """Test comma join list with multi items with empty=True."""
        r = tools.join_comma(obj=["x", "", "a", None, "c"], empty=True)
        assert r == "x, , a, None, c"

    def test_single(self):
        """Test comma join list with single item."""
        r = tools.join_comma(obj=["x"])
        assert r == "x"

    def test_non_list(self):
        """Test comma non list."""
        r = tools.join_comma(obj="x")
        assert r == "x"

    def test_empty_list(self):
        """Test comma empty list."""
        r = tools.join_comma(obj=[])
        assert r == ""

    def test_single_none(self):
        """Test comma join with None."""
        r = tools.join_comma(obj=None)
        assert r == ""


class TestJoinCr(object):
    """Test axonius_api_client.tools.join_cr."""

    def test_multi(self):
        """Test cr join multi."""
        r = tools.join_cr(obj=["x", "a", "c"])
        assert r == "\n  x\n  a\n  c"

    def test_single(self):
        """Test cr join multi."""
        r = tools.join_cr(obj=["x"])
        assert r == "\n  x"

    def test_single_non_list(self):
        """Test cr join list w/ single entry."""
        r = tools.join_cr(obj="x")
        assert r == "\n  x"

    def test_single_empty_list(self):
        """Test cr join empty list."""
        r = tools.join_cr(obj=[])
        assert r == ""

    def test_single_none(self):
        """Test cr join with None."""
        r = tools.join_cr(obj=None)
        assert r == ""

    def test_post_and_pre(self):
        """Test cr join with post and pre = True."""
        r = tools.join_cr(obj=["x", "a", "c"], pre=True, post=True)
        assert r == "\n  x\n  a\n  c\n  "


class TestPath(object):
    """Test axonius_api_client.tools.path."""

    def test_str(self):
        """Test resolve with a string."""
        r = tools.path(obj="/../badwolf")
        assert isinstance(r, tools.pathlib.Path)
        assert format(r) == format("/badwolf")

    def test_pathlib(self):
        """Test resolve with a pathlib.Path."""
        r = tools.path(obj=tools.pathlib.Path("."))
        assert isinstance(r, tools.pathlib.Path)

    def test_user(self):
        """Test resolve with ~."""
        r = tools.path(obj="~")
        assert isinstance(r, tools.pathlib.Path)
        assert format(r) == format(tools.pathlib.Path.home())


class TestPathWrite(object):
    """Test axonius_api_client.tools.path_write."""

    def test_simple_pathlib(self, tmp_path):
        """Test simple write with pathlib object."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = tools.path_write(obj=path, data=data)
        assert ret_path.read_text() == data
        assert format(ret_path) == format(path)
        assert ret_write == len(data)
        assert ret_path.stat().st_mode == 33152
        assert ret_path.parent.stat().st_mode == 16832

    def test_simple_str(self, tmp_path):
        """Test simple write with path as str."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = tools.path_write(obj=format(path), data=data)
        assert ret_path.read_text() == data
        assert format(ret_path) == format(path)
        assert ret_write == len(data)

    def test_parent_fail(self, tmp_path):
        """Test simple write with pathlib object."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        with pytest.raises(exceptions.ToolsError):
            tools.path_write(obj=path, data=data, make_parent=False)

    def test_noperm_parent(self):
        """Pass."""
        tmpdir = tools.pathlib.Path(tempfile.gettempdir())
        path = tmpdir / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = tools.path_write(obj=path, data=data, overwrite=True)
        assert ret_path.read_text() == data

    def test_overwrite_false(self, tmp_path):
        """Test overwrite=False."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        tools.path_write(obj=path, data=data)
        with pytest.raises(exceptions.ToolsError):
            tools.path_write(obj=path, data=data, overwrite=False)

    def test_overwrite_true(self, tmp_path):
        """Test overwrite=True."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        tools.path_write(obj=path, data=data)
        tools.path_write(obj=path, data=data, overwrite=True)
        assert path.is_file()

    def test_binary_true_nonbinary(self, tmp_path):
        """Test binary=True with nonbinary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = tools.path_write(obj=path, data=data, binary=True)
        assert ret_path.read_text() == data
        assert ret_path.read_bytes() == data.encode()

    def test_binary_true_binary(self, tmp_path):
        """Test binary=True with binary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = b"abc\n123\n"
        ret_path, ret_write = tools.path_write(obj=path, data=data, binary=True)
        assert ret_path.read_text() == data.decode()
        assert ret_path.read_bytes() == data

    def test_binary_false_nonbinary(self, tmp_path):
        """Test binary=False with nonbinary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = tools.path_write(obj=path, data=data, binary=False)
        assert ret_path.read_text() == data
        assert ret_path.read_bytes() == data.encode()

    def test_binary_false_binary(self, tmp_path):
        """Test binary=False with binary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = b"abc\n123\n"
        ret_path, ret_write = tools.path_write(obj=path, data=data, binary=False)
        assert ret_path.read_text() == data.decode()
        assert ret_path.read_bytes() == data

    def test_is_json_false_dotjson_nonjson(self, tmp_path):
        """Test is_json=False with .json in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = b""
        ret_path, ret_write = tools.path_write(obj=path, data=data, is_json=False)
        assert ret_path.read_text() == data.decode()

    def test_is_json_false_dotjson_json(self, tmp_path):
        """Test is_json=False with .json in filename and valid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = {"x": 2}
        ret_path, ret_write = tools.path_write(obj=path, data=data, is_json=False)
        assert ret_path.read_text() == '{\n  "x": 2\n}'

    def test_is_json_true_nonjson(self, tmp_path):
        """Test is_json=True with .json not in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.text"
        data = pytest
        with pytest.raises(Exception):
            tools.path_write(obj=path, data=data, is_json=True)

    def test_is_json_true_json(self, tmp_path):
        """Test is_json=True with .json not in filename and valid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.text"
        data = {"x": 2}
        ret_path, ret_write = tools.path_write(obj=path, data=data, is_json=True)
        assert ret_path.read_text() == '{\n  "x": 2\n}'


class TestPathRead(object):
    """Test axonius_api_client.tools.path_read."""

    def test_pathlib(self, tmp_path):
        """Test simple write with pathlib object."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path_write(obj=path, data=data)
        rret_path, ret_read = tools.path_read(obj=path)
        assert wret_path == rret_path
        assert ret_read == data

    def test_str(self, tmp_path):
        """Test simple write with str."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path_write(obj=path, data=data)
        rret_path, ret_read = tools.path_read(obj=format(path))
        assert wret_path == rret_path
        assert ret_read == data

    def test_binary_true(self, tmp_path):
        """Test binary=True."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path_write(obj=path, data=data)
        rret_path, ret_read = tools.path_read(obj=format(path), binary=True)
        assert wret_path == rret_path
        assert ret_read == data.encode()

    def test_binary_false(self, tmp_path):
        """Test binary=False."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path_write(obj=path, data=data)
        rret_path, ret_read = tools.path_read(obj=format(path), binary=False)
        assert wret_path == rret_path
        assert ret_read == data

    def test_is_json_true_nonjson(self, tmp_path):
        """Test is_json=True with .json not in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.text"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path_write(obj=path, data=data)
        with pytest.raises(Exception):
            tools.path_read(obj=path, is_json=True)

    def test_is_json_false_dotjson_nonjson(self, tmp_path):
        """Test is_json=False with .json in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path_write(obj=path, data=data)
        rret_path, ret_read = tools.path_read(obj=path, is_json=False)
        assert wret_path == rret_path
        assert ret_read == data

    def test_is_json_false_dotjson_json(self, tmp_path):
        """Test is_json=False with .json in filename and valid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = {"x": 2}
        wret_path, ret_write = tools.path_write(obj=path, data=data)
        rret_path, ret_read = tools.path_read(obj=path, is_json=False)
        assert wret_path == rret_path
        assert ret_read == data

    def test_not_found(self, tmp_path):
        """Test is_json=False with .json in filename and valid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        with pytest.raises(exceptions.ToolsError):
            tools.path_read(obj=path)


class TestGrouper(object):
    """Test tools.grouper."""

    def test_iter(self):
        """Simple test."""
        x = list(tools.grouper([1, 2, 3, 4, 5, 6], 2))
        assert x == [(1, 2), (3, 4), (5, 6)]

    def test_iter_off1(self):
        """Simple test."""
        x = list(tools.grouper([1, 2, 3, 4, 5, 6, 7], 2))
        assert x == [(1, 2), (3, 4), (5, 6), (7, None)]

    def test_iter_off1_strfill(self):
        """Simple test."""
        x = list(tools.grouper([1, 2, 3, 4, 5, 6, 7], 2, "x"))
        assert x == [(1, 2), (3, 4), (5, 6), (7, "x")]


class TestNestDepth(object):
    """Test tools.listify."""

    def test_dict1(self):
        """Simple test."""
        x = tools.nest_depth(obj={"x": 1, "y": 1})
        assert x == 1

    def test_dict2(self):
        """Simple test."""
        x = tools.nest_depth(obj={"x": 1, "y": {"z": 1}})
        assert x == 2

    def test_tuple(self):
        """Simple test."""
        x = tools.nest_depth(obj=(1, 2))
        assert x == 1

    def test_list1(self):
        """Simple test."""
        x = tools.nest_depth(obj=[1, 2])
        assert x == 1

    def test_list2(self):
        """Simple test."""
        x = tools.nest_depth(obj=[[1], [2]])
        assert x == 2

    @pytest.mark.parametrize("val", [1, "1", None], scope="class")
    def test_not_complex(self, val):
        """Simple test."""
        x = tools.nest_depth(obj=val)
        assert x == 0

    def test_mix(self):
        """Simple test."""
        x = tools.nest_depth(obj=["1", ["a", {}]])
        assert x == 3


class TestListify(object):
    """Test tools.listify."""

    def test_dict_keys(self):
        """Simple test."""
        x = tools.listify(obj={"x": 1, "y": 1}, dictkeys=True)
        assert x == ["x", "y"]

    def test_dict_notkeys(self):
        """Simple test."""
        x = tools.listify(obj={"x": 1, "y": 1}, dictkeys=False)
        assert x == [{"x": 1, "y": 1}]

    def test_tuple(self):
        """Simple test."""
        x = tools.listify(obj=(1, 2))
        assert x == [1, 2]

    def test_list(self):
        """Simple test."""
        x = tools.listify(obj=[1, 2])
        assert x == [1, 2]

    def test_int(self):
        """Simple test."""
        x = tools.listify(obj=1)
        assert x == [1]

    def test_str(self):
        """Simple test."""
        x = tools.listify(obj="1")
        assert x == ["1"]

    def test_none(self):
        """Simple test."""
        x = tools.listify(obj=None)
        assert x == []


class TestIsInt(object):
    """Test tools.is_*."""

    @pytest.mark.parametrize("ok", [0, 4], scope="class")
    @pytest.mark.parametrize("bad", ["1", False, True, b"1"], scope="class")
    def test_int_digit_false(self, ok, bad):
        """Simple test."""
        assert tools.is_int(obj=ok, digit=False)
        assert not tools.is_int(obj=bad, digit=False)

    @pytest.mark.parametrize("ok", [0, 4, "1", b"1"], scope="class")
    @pytest.mark.parametrize("bad", [False, True, {}, "x", b"x"], scope="class")
    def test_int_digit_true(self, ok, bad):
        """Simple test."""
        assert tools.is_int(obj=ok, digit=True)
        assert not tools.is_int(obj=bad, digit=True)


class TestStripLeft(object):
    """Test tools.strip_left."""

    def test_left_str(self):
        """Simple test."""
        x = "badwolfbadwolf"
        y = tools.strip_left(obj=x, fix="badwolf")
        assert y == "badwolf"

    def test_left_list(self):
        """Simple test."""
        x = ["badwolfbadwolf", "badwolf", "abadwolfbadwolf"]
        y = tools.strip_left(obj=x, fix="badwolf")
        assert y == ["badwolf", "", "abadwolfbadwolf"]

    def test_left_str_nomatch(self):
        """Simple test."""
        x = "abadwolfbadwolf"
        y = tools.strip_left(obj=x, fix="badwolf")
        assert y == "abadwolfbadwolf"


class TestStripRight(object):
    """Test tools.strip_right."""

    def test_right_str(self):
        """Simple test."""
        x = "badwolfbadwolf"
        y = tools.strip_right(obj=x, fix="badwolf")
        assert y == "badwolf"

    def test_right_str_nomatch(self):
        """Simple test."""
        x = "badwolfbadwolfa"
        y = tools.strip_right(obj=x, fix="badwolf")
        assert y == "badwolfbadwolfa"

    def test_right_list(self):
        """Simple test."""
        x = ["badwolfbadwolf", "badwolf", "badwolfbadwolfa"]
        y = tools.strip_right(obj=x, fix="badwolf")
        assert y == ["badwolf", "", "badwolfbadwolfa"]


class TestJsonLoad(object):
    """Test tools.json_load."""

    def test_load(self):
        """Simple test."""
        x = "{}"
        y = tools.json_load(obj=x)
        assert y == {}

    def test_load_error_false(self):
        """Simple test."""
        x = "xxx"
        y = tools.json_load(obj=x, error=False)
        assert y == "xxx"

    def test_load_error_true(self):
        """Simple test."""
        x = "xxx"
        with pytest.raises(Exception):
            tools.json_load(obj=x, error=True)


class TestJsonDump(object):
    """Test tools.json_dump."""

    def test_dump(self):
        """Simple test."""
        x = {"x": 2}
        y = tools.json_dump(obj=x)
        assert y == '{\n  "x": 2\n}'

    def test_dump_error_false(self):
        """Simple test."""
        x = pytest
        y = tools.json_dump(obj=x, error=False)
        assert y == pytest

    def test_dump_error_true(self):
        """Simple test."""
        x = pytest
        with pytest.raises(Exception):
            tools.json_dump(obj=x, error=True)


class TestJsonReload(object):
    """Test tools.json_dump."""

    def test_re_load(self):
        """Simple test."""
        x = '{"x": 2}'
        y = tools.json_reload(obj=x)
        assert y == '{\n  "x": 2\n}'

    def test_re_load_error_false(self):
        """Simple test."""
        x = "{"
        y = tools.json_reload(obj=x, error=False)
        assert y == x

    def test_re_load_error_true(self):
        """Simple test."""
        x = "{"
        with pytest.raises(Exception):
            tools.json_reload(obj=x, error=True)


class TestDtMinAgo(object):
    """Test tools.dt_*."""

    def test_min_ago_utc_str(self):
        """Simple test."""
        then = format(tools.dt_now() - tools.timedelta(minutes=1))
        assert tools.dt_min_ago(obj=then) == 1

    def test_min_ago_utc_dt(self):
        """Simple test."""
        then = tools.dt_now() - tools.timedelta(minutes=1)
        assert tools.dt_min_ago(obj=then) == 1

    def test_min_ago_utc_dt_naive(self):
        """Simple test."""
        then = tools.dt_now(None) - tools.timedelta(minutes=1)
        assert tools.dt_min_ago(obj=then) == 1

    def test_min_ago_utc_dtdelta(self):
        """Simple test."""
        then = tools.timedelta(minutes=3)
        assert tools.dt_min_ago(obj=then) == 3

    def test_min_ago_naive(self):
        """Simple test."""
        then = tools.datetime.now() - tools.timedelta(minutes=1)
        assert tools.dt_min_ago(obj=format(then)) == 1


class TestDtNow(object):
    """Test tools.dt_*."""

    def test_now(self):
        """Pass."""
        now = tools.dt_now()
        assert now.tzinfo

    def test_now_notz(self):
        """Pass."""
        now = tools.dt_now(tz=None)
        assert not now.tzinfo

    def test_now_delta(self):
        """Pass."""
        then = tools.dt_now(delta=tools.timedelta(minutes=5))
        assert tools.dt_min_ago(then) == 5


class TestDtParse(object):
    """Test tools.dt_*."""

    @pytest.mark.parametrize(
        "val",
        [format(tools.dt_now()), tools.dt_now(), tools.timedelta(minutes=1)],
        scope="class",
    )
    def test_val(self, val):
        """Pass."""
        now = tools.dt_parse(obj=val)
        assert isinstance(now, tools.datetime)

    def test_list(self):
        """Pass."""
        now = [format(tools.dt_now())]
        now = tools.dt_parse(obj=now)
        assert isinstance(now, tools.LIST)
        assert [isinstance(x, tools.datetime) for x in now]


class TestDtWithinMin(object):
    """Test tools.dt_*."""

    @pytest.mark.parametrize(
        "val", [None, "x", False, True, {}, [], 6, "8", b"9"], scope="class"
    )
    def test_bad(self, val):
        """Pass."""
        then = tools.dt_now(delta=tools.timedelta(minutes=5))
        assert tools.dt_within_min(obj=then, n=val) is False

    @pytest.mark.parametrize("val", [0, 4, "1", b"2"], scope="class")
    def test_ok(self, val):
        """Pass."""
        then = tools.dt_now(delta=tools.timedelta(minutes=5))
        assert tools.dt_within_min(obj=then, n=val) is True
