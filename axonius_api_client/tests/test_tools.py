# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import logging
import tempfile
import time

import pytest
import six

import axonius_api_client as axonapi

tools = axonapi.tools

BAD_CRED = "tardis"


class TestJoinUrl(object):
    """Test axonius_api_client.tools.join.url."""

    def test_url(self):
        """Test url gets joined properly no matter the slashes."""
        r = tools.join.url("https://test.com")
        assert r == "https://test.com/"
        r = tools.join.url("https://test.com/")
        assert r == "https://test.com/"
        r = tools.join.url("https://test.com////")
        assert r == "https://test.com/"
        r = tools.join.url("https://test.com", "")
        assert r == "https://test.com/"
        r = tools.join.url("https://test.com", "", "")
        assert r == "https://test.com/"
        r = tools.join.url("https://test.com", "/", "")
        assert r == "https://test.com/"
        r = tools.join.url("https://test.com", "/", "/")
        assert r == "https://test.com/"

    def test_url_path(self):
        """Test url, path gets joined properly no matter the slashes."""
        r = tools.join.url("https://test.com", "a")
        assert r == "https://test.com/a"
        r = tools.join.url("https://test.com", "/a")
        assert r == "https://test.com/a"
        r = tools.join.url("https://test.com", "//a")
        assert r == "https://test.com/a"
        r = tools.join.url("https://test.com", "a/")
        assert r == "https://test.com/a/"
        r = tools.join.url("https://test.com", "a/b")
        assert r == "https://test.com/a/b"
        r = tools.join.url("https://test.com", "a/b", "")
        assert r == "https://test.com/a/b"
        r = tools.join.url("https://test.com", "a/b/", "")
        assert r == "https://test.com/a/b/"
        r = tools.join.url("https://test.com", "a/b", "/")
        assert r == "https://test.com/a/b/"
        r = tools.join.url("https://test.com", "a/b", "/////")
        assert r == "https://test.com/a/b/"

    def test_url_path_route(self):
        """Test url, path, route gets joined properly no matter the slashes."""
        r = tools.join.url("https://test.com", "a", "b")
        assert r == "https://test.com/a/b"
        r = tools.join.url("https://test.com", "/a", "b")
        assert r == "https://test.com/a/b"
        r = tools.join.url("https://test.com", "//a", "b")
        assert r == "https://test.com/a/b"
        r = tools.join.url("https://test.com", "a", "b/c/d")
        assert r == "https://test.com/a/b/c/d"


class TestJoinDot(object):
    """Test axonius_api_client.tools.join.dot."""

    def test_multi(self):
        """Test dot join multi."""
        r = tools.join.dot(["x", "a", "c"])
        assert r == "x.a.c"

    def test_multi_with_empty_false(self):
        """Test dot join multi with empty=False."""
        r = tools.join.dot(["x", "", "a", None, "c", []], empty=False)
        assert r == "x.a.c"

    def test_multi_with_empty_true(self):
        """Test dot join multi with empty=True."""
        r = tools.join.dot(["x", "", "a", None, "c"], empty=True)
        assert r == "x..a.None.c"

    def test_single(self):
        """Test dot join single."""
        r = tools.join.dot(["x"])
        assert r == "x"

    def test_non_list(self):
        """Test dot join single."""
        r = tools.join.dot("x")
        assert r == "x"

    def test_empty_list(self):
        """Test dot join single."""
        r = tools.join.dot([])
        assert r == ""

    def test_single_None(self):
        """Test cr join with None."""
        r = tools.join.cr(None)
        assert r == ""


class TestJoinComma(object):
    """Test axonius_api_client.tools.join.dot."""

    def test_multi(self):
        """Test comma join multi."""
        r = tools.join.comma(["x", "a", "c"])
        assert r == "x, a, c"

    def test_multi_no_indent(self):
        """Test comma join multi with indent=False."""
        r = tools.join.comma(["x", "a", "c"], indent=False)
        assert r == "x,a,c"

    def test_multi_with_empty_false(self):
        """Test comma join multi with empty=False."""
        r = tools.join.comma(["x", "", "a", None, "c", []], empty=False)
        assert r == "x, a, c"

    def test_multi_with_empty_true(self):
        """Test comma join list with multi items with empty=True."""
        r = tools.join.comma(["x", "", "a", None, "c"], empty=True)
        assert r == "x, , a, None, c"

    def test_single(self):
        """Test comma join list with single item."""
        r = tools.join.comma(["x"])
        assert r == "x"

    def test_non_list(self):
        """Test comma non list."""
        r = tools.join.comma("x")
        assert r == "x"

    def test_empty_list(self):
        """Test comma empty list."""
        r = tools.join.comma([])
        assert r == ""

    def test_single_None(self):
        """Test comma join with None."""
        r = tools.join.comma(None)
        assert r == ""


class TestJoinCr(object):
    """Test axonius_api_client.tools.join.cr."""

    def test_multi(self):
        """Test cr join multi."""
        r = tools.join.cr(["x", "a", "c"])
        assert r == "\n  x\n  a\n  c"

    def test_single(self):
        """Test cr join multi."""
        r = tools.join.cr(["x"])
        assert r == "\n  x"

    def test_single_non_list(self):
        """Test cr join list w/ single entry."""
        r = tools.join.cr("x")
        assert r == "\n  x"

    def test_single_empty_list(self):
        """Test cr join empty list."""
        r = tools.join.cr([])
        assert r == ""

    def test_single_None(self):
        """Test cr join with None."""
        r = tools.join.cr(None)
        assert r == ""

    def test_post_and_pre(self):
        """Test cr join with post and pre = True."""
        r = tools.join.cr(["x", "a", "c"], pre=True, post=True)
        assert r == "\n  x\n  a\n  c\n  "


class TestPathResolve(object):
    """Test axonius_api_client.tools.path.resolve."""

    def test_str(self):
        """Test resolve with a string."""
        r = tools.path.resolve("/../badwolf")
        assert isinstance(r, tools.pathlib.Path)
        assert format(r) == format("/badwolf")

    def test_pathlib(self):
        """Test resolve with a pathlib.Path."""
        r = tools.path.resolve(tools.pathlib.Path("."))
        assert isinstance(r, tools.pathlib.Path)

    def test_user(self):
        """Test resolve with ~."""
        r = tools.path.resolve("~")
        assert isinstance(r, tools.pathlib.Path)
        assert format(r) == format(tools.pathlib.Path.home())


class TestPathGet(object):
    """Test axonius_api_client.tools.path.get."""

    def test_str(self):
        """Test get with a string."""
        r = tools.path.get("/../badwolf")
        assert isinstance(r, tools.pathlib.Path)

    def test_pathlib(self):
        """Test get with a pathlib.Path."""
        r = tools.path.get(tools.pathlib.Path("."))
        assert isinstance(r, tools.pathlib.Path)


class TestPathWrite(object):
    """Test axonius_api_client.tools.path.write."""

    def test_simple_pathlib(self, tmp_path):
        """Test simple write with pathlib object."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = tools.path.write(obj=path, data=data)
        assert ret_path.read_text() == data
        assert format(ret_path) == format(path)
        assert ret_write == len(data)
        # FUTURE: unsure if these are same on windows
        assert ret_path.stat().st_mode == 33152
        assert ret_path.parent.stat().st_mode == 16832

    def test_simple_str(self, tmp_path):
        """Test simple write with path as str."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = tools.path.write(obj=format(path), data=data)
        assert ret_path.read_text() == data
        assert format(ret_path) == format(path)
        assert ret_write == len(data)

    def test_parent_fail(self, tmp_path):
        """Test simple write with pathlib object."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        with pytest.raises(axonapi.exceptions.ToolsError):
            tools.path.write(obj=path, data=data, make_parent=False)

    def test_noperm_parent(self):
        """Pass."""
        tmpdir = tools.pathlib.Path(tempfile.gettempdir())
        path = tmpdir / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = tools.path.write(obj=path, data=data, overwrite=True)
        assert ret_path.read_text() == data

    def test_overwrite_false(self, tmp_path):
        """Test overwrite=False."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        tools.path.write(obj=path, data=data)
        with pytest.raises(axonapi.exceptions.ToolsError):
            tools.path.write(obj=path, data=data, overwrite=False)

    def test_overwrite_true(self, tmp_path):
        """Test overwrite=True."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        tools.path.write(obj=path, data=data)
        tools.path.write(obj=path, data=data, overwrite=True)
        assert path.is_file()

    def test_binary_true_nonbinary(self, tmp_path):
        """Test binary=True with nonbinary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = tools.path.write(obj=path, data=data, binary=True)
        assert ret_path.read_text() == data
        assert ret_path.read_bytes() == data.encode()

    def test_binary_true_binary(self, tmp_path):
        """Test binary=True with binary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = b"abc\n123\n"
        ret_path, ret_write = tools.path.write(obj=path, data=data, binary=True)
        assert ret_path.read_text() == data.decode()
        assert ret_path.read_bytes() == data

    def test_binary_false_nonbinary(self, tmp_path):
        """Test binary=False with nonbinary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        ret_path, ret_write = tools.path.write(obj=path, data=data, binary=False)
        assert ret_path.read_text() == data
        assert ret_path.read_bytes() == data.encode()

    def test_binary_false_binary(self, tmp_path):
        """Test binary=False with binary data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = b"abc\n123\n"
        ret_path, ret_write = tools.path.write(obj=path, data=data, binary=False)
        assert ret_path.read_text() == data.decode()
        assert ret_path.read_bytes() == data

    def test_is_json_false_dotjson_nonjson(self, tmp_path):
        """Test is_json=False with .json in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = b""
        ret_path, ret_write = tools.path.write(obj=path, data=data, is_json=False)
        assert ret_path.read_text() == data.decode()

    def test_is_json_false_dotjson_json(self, tmp_path):
        """Test is_json=False with .json in filename and valid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = {"x": 2}
        ret_path, ret_write = tools.path.write(obj=path, data=data, is_json=False)
        assert ret_path.read_text() == '{\n  "x": 2\n}'

    def test_is_json_true_nonjson(self, tmp_path):
        """Test is_json=True with .json not in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.text"
        data = pytest
        with pytest.raises(Exception):
            tools.path.write(obj=path, data=data, is_json=True)

    def test_is_json_true_json(self, tmp_path):
        """Test is_json=True with .json not in filename and valid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.text"
        data = {"x": 2}
        ret_path, ret_write = tools.path.write(obj=path, data=data, is_json=True)
        assert ret_path.read_text() == '{\n  "x": 2\n}'


class TestPathRead(object):
    """Test axonius_api_client.tools.path.read."""

    def test_simple_pathlib(self, tmp_path):
        """Test simple write with pathlib object."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path.write(obj=path, data=data)
        rret_path, ret_read = tools.path.read(obj=path)
        assert wret_path == rret_path
        assert ret_read == data

    def test_simple_str(self, tmp_path):
        """Test simple write with str."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path.write(obj=path, data=data)
        rret_path, ret_read = tools.path.read(obj=format(path))
        assert wret_path == rret_path
        assert ret_read == data

    def test_binary_true(self, tmp_path):
        """Test binary=True."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path.write(obj=path, data=data)
        rret_path, ret_read = tools.path.read(obj=format(path), binary=True)
        assert wret_path == rret_path
        assert ret_read == data.encode()

    def test_binary_false(self, tmp_path):
        """Test binary=False."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path.write(obj=path, data=data)
        rret_path, ret_read = tools.path.read(obj=format(path), binary=False)
        assert wret_path == rret_path
        assert ret_read == data

    def test_is_json_true_nonjson(self, tmp_path):
        """Test is_json=True with .json not in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.text"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path.write(obj=path, data=data)
        with pytest.raises(Exception):
            tools.path.read(obj=path, is_json=True)

    def test_is_json_false_dotjson_nonjson(self, tmp_path):
        """Test is_json=False with .json in filename and invalid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = "abc\n123\n"
        wret_path, ret_write = tools.path.write(obj=path, data=data)
        rret_path, ret_read = tools.path.read(obj=path, is_json=False)
        assert wret_path == rret_path
        assert ret_read == data

    def test_is_json_false_dotjson_json(self, tmp_path):
        """Test is_json=False with .json in filename and valid json data."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.json"
        data = {"x": 2}
        wret_path, ret_write = tools.path.write(obj=path, data=data)
        rret_path, ret_read = tools.path.read(obj=path, is_json=False)
        assert wret_path == rret_path
        assert ret_read == data


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
        x = tools.nest_depth({"x": 1, "y": 1})
        assert x == 1

    def test_dict2(self):
        """Simple test."""
        x = tools.nest_depth({"x": 1, "y": {"z": 1}})
        assert x == 2

    def test_tuple(self):
        """Simple test."""
        x = tools.nest_depth((1, 2))
        assert x == 1

    def test_list1(self):
        """Simple test."""
        x = tools.nest_depth([1, 2])
        assert x == 1

    def test_list2(self):
        """Simple test."""
        x = tools.nest_depth([[1], [2]])
        assert x == 2

    def test_int(self):
        """Simple test."""
        x = tools.nest_depth(1)
        assert x == 0

    def test_str(self):
        """Simple test."""
        x = tools.nest_depth("1")
        assert x == 0

    def test_none(self):
        """Simple test."""
        x = tools.nest_depth(None)
        assert x == 0


class TestValuesMatch(object):
    """Test tools.values_match."""

    def test_no_case_no_regex(self):
        """Simple test."""
        x = tools.values_match(
            checks="x", values="x", use_regex=False, ignore_case=False
        )
        assert x
        x = tools.values_match(
            checks="x", values="X", use_regex=False, ignore_case=False
        )
        assert not x
        x = tools.values_match(
            checks="x", values=["X"], use_regex=False, ignore_case=False
        )
        assert not x
        x = tools.values_match(
            checks="x", values=["X", "x"], use_regex=False, ignore_case=False
        )
        assert not x

    def test_case_no_regex(self):
        """Simple test."""
        x = tools.values_match(
            checks="x", values="X", use_regex=False, ignore_case=True
        )
        assert x
        x = tools.values_match(
            checks="x", values="x", use_regex=False, ignore_case=True
        )
        assert x
        x = tools.values_match(
            checks="x", values="xxxxx", use_regex=False, ignore_case=True
        )
        assert not x
        x = tools.values_match(
            checks="x", values=["X"], use_regex=False, ignore_case=True
        )
        assert x
        x = tools.values_match(
            checks="x", values=["X", "x"], use_regex=False, ignore_case=True
        )
        assert x
        x = tools.values_match(
            checks="x", values=["A", "a"], use_regex=False, ignore_case=True
        )
        assert not x

    def test_case_regex(self):
        """Simple test."""
        x = tools.values_match(checks="x", values="X", use_regex=True, ignore_case=True)
        assert x
        x = tools.values_match(
            checks=".*", values="X", use_regex=True, ignore_case=True
        )
        assert x
        x = tools.values_match(checks="x", values="x", use_regex=True, ignore_case=True)
        assert x
        x = tools.values_match(
            checks="x", values="xxxxx", use_regex=True, ignore_case=True
        )
        assert x
        x = tools.values_match(
            checks="x", values=["X"], use_regex=True, ignore_case=True
        )
        assert x
        x = tools.values_match(
            checks="x", values=["X", "x"], use_regex=True, ignore_case=True
        )
        assert x
        x = tools.values_match(
            checks="x", values=["A", "a"], use_regex=True, ignore_case=True
        )
        assert not x

    def test_no_case_regex(self):
        """Simple test."""
        x = tools.values_match(
            checks="x", values="X", use_regex=True, ignore_case=False
        )
        assert not x
        x = tools.values_match(
            checks=".*", values="X", use_regex=True, ignore_case=False
        )
        assert x
        x = tools.values_match(
            checks="x", values="x", use_regex=True, ignore_case=False
        )
        assert x
        x = tools.values_match(
            checks="x", values="xxxxx", use_regex=True, ignore_case=False
        )
        assert x
        x = tools.values_match(
            checks="x", values=["X"], use_regex=True, ignore_case=False
        )
        assert not x
        x = tools.values_match(
            checks="x", values=["X", "x"], use_regex=True, ignore_case=False
        )
        assert not x
        x = tools.values_match(
            checks="x", values=["A", "a"], use_regex=True, ignore_case=False
        )
        assert not x


class TestListify(object):
    """Test tools.listify."""

    def test_dict(self):
        """Simple test."""
        x = tools.listify({"x": 1, "y": 1})
        assert x == ["x", "y"]

    def test_dict_notkeys(self):
        """Simple test."""
        x = tools.listify({"x": 1, "y": 1}, dictkeys=False)
        assert x == [{"x": 1, "y": 1}]

    def test_tuple(self):
        """Simple test."""
        x = tools.listify((1, 2))
        assert x == [1, 2]

    def test_list(self):
        """Simple test."""
        x = tools.listify([1, 2])
        assert x == [1, 2]

    def test_int(self):
        """Simple test."""
        x = tools.listify(1)
        assert x == [1]

    def test_str(self):
        """Simple test."""
        x = tools.listify("1")
        assert x == ["1"]

    def test_none(self):
        """Simple test."""
        x = tools.listify(None)
        assert x == []


class TestIsType(object):
    """Test tools.is_type."""

    def test_bytes(self):
        """Simple test."""
        x = b"2"
        assert tools.is_type.bytes(x)
        assert not tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert not tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert not tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert not tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert not tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_str(self):
        """Simple test."""
        x = "x"
        assert not tools.is_type.bytes(x)
        assert tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert not tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert not tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert not tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_str_empty(self):
        """Simple test."""
        x = ""
        assert not tools.is_type.bytes(x)
        assert tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert not tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert not tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_str_int(self):
        """Simple test."""
        x = "2"
        assert not tools.is_type.bytes(x)
        assert tools.is_type.str(x)
        assert tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert not tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert not tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert not tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_int(self):
        """Simple test."""
        x = 0
        assert not tools.is_type.bytes(x)
        assert not tools.is_type.str(x)
        assert tools.is_type.str_int(x)
        assert tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert not tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert not tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert not tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_float(self):
        """Simple test."""
        x = 0.0
        assert not tools.is_type.bytes(x)
        assert not tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert not tools.is_type.list(x)
        assert tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert not tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert not tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_dict_empty(self):
        """Simple test."""
        x = {}
        assert not tools.is_type.bytes(x)
        assert not tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert not tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert not tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_dict(self):
        """Simple test."""
        x = {"x": 2}
        assert not tools.is_type.bytes(x)
        assert not tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert not tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert not tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert not tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_tuple(self):
        """Simple test."""
        x = (1, None)
        assert not tools.is_type.bytes(x)
        assert not tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert tools.is_type.tuple(x)
        assert tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert not tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert not tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_tuple_empty(self):
        """Simple test."""
        x = ()
        assert not tools.is_type.bytes(x)
        assert not tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert tools.is_type.tuple(x)
        assert tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert not tools.is_type.simple(x)
        assert tools.is_type.lot(x, tools.is_type.str)
        assert tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_list(self):
        """Simple test."""
        x = [1, None]
        assert not tools.is_type.bytes(x)
        assert not tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert not tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert not tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_list_empty(self):
        """Simple test."""
        x = []
        assert not tools.is_type.bytes(x)
        assert not tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert not tools.is_type.simple(x)
        assert tools.is_type.lot(x, tools.is_type.str)
        assert tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_none(self):
        """Simple test."""
        x = None
        assert not tools.is_type.bytes(x)
        assert not tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert not tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert tools.is_type.none(x)
        assert tools.is_type.empty(x)
        assert not tools.is_type.bool(x)
        assert not tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert not tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_empty(self):
        """Simple test."""
        assert tools.is_type.empty("")
        assert tools.is_type.empty(None)
        assert tools.is_type.empty([])
        assert tools.is_type.empty(())
        assert tools.is_type.empty({})
        assert not tools.is_type.empty([1])
        assert not tools.is_type.empty((1,))
        assert not tools.is_type.empty({"x": 1})
        assert not tools.is_type.empty("1")

    def test_bool(self):
        """Simple test."""
        x = True
        assert not tools.is_type.bytes(x)
        assert not tools.is_type.str(x)
        assert not tools.is_type.str_int(x)
        assert not tools.is_type.int(x)
        assert not tools.is_type.dict(x)
        assert not tools.is_type.tuple(x)
        assert not tools.is_type.list(x)
        assert not tools.is_type.float(x)
        assert not tools.is_type.none(x)
        assert not tools.is_type.empty(x)
        assert tools.is_type.bool(x)
        assert tools.is_type.simple(x)
        assert not tools.is_type.lot(x, tools.is_type.str)
        assert not tools.is_type.los(x)
        assert not tools.is_type.lod(x)
        assert not tools.is_type.lol(x)
        assert not tools.is_type.lols(x)
        assert not tools.is_type.dt(x)
        assert not tools.is_type.dtdelta(x)
        assert not tools.is_type.complex(x)
        assert not tools.is_type.path(x)

    def test_simple(self):
        """Simple test."""
        assert tools.is_type.simple("")
        assert tools.is_type.simple(1)
        assert tools.is_type.simple(True)
        assert tools.is_type.simple(False)
        assert tools.is_type.simple(0.1)
        assert not tools.is_type.simple([1])
        assert not tools.is_type.simple((1,))
        assert not tools.is_type.simple({"x": 1})
        assert not tools.is_type.simple(None)

    def test_lot(self):
        """Simple test."""
        assert tools.is_type.lot([""], tools.is_type.str)
        assert tools.is_type.lot(["1"], tools.is_type.str)
        assert tools.is_type.lot([], tools.is_type.str)
        assert not tools.is_type.lot([None], tools.is_type.str)
        assert not tools.is_type.lot([[]], tools.is_type.str)

    def test_los(self):
        """Simple test."""
        assert tools.is_type.los([""])
        assert tools.is_type.los(["1"])
        assert tools.is_type.los([])
        assert not tools.is_type.los([None])
        assert not tools.is_type.los([[]])

    def test_lod(self):
        """Simple test."""
        assert tools.is_type.lod([{"x": 1}])
        assert tools.is_type.lod([{}])
        assert not tools.is_type.lod([])
        assert not tools.is_type.lod([None])
        assert not tools.is_type.lod([[]])

    def test_lol(self):
        """Simple test."""
        assert tools.is_type.lol([[1]])
        assert tools.is_type.lol([[None]])
        assert not tools.is_type.lol([{}])
        assert not tools.is_type.lol([None])

    def test_lols(self):
        """Simple test."""
        assert tools.is_type.lols([[1]])
        assert tools.is_type.lols([["1"]])
        assert not tools.is_type.lols([["1", None]])
        assert not tools.is_type.lols([{}])
        assert not tools.is_type.lols([None])

    def test_dt(self):
        """Simple test."""
        assert tools.is_type.dt(datetime.datetime.now())
        assert tools.is_type.dt(datetime.datetime.utcnow())
        assert not tools.is_type.dt(datetime.timedelta())

    def test_dtdelta(self):
        """Simple test."""
        assert not tools.is_type.dtdelta(datetime.datetime.now())
        assert not tools.is_type.dtdelta(datetime.datetime.utcnow())
        assert tools.is_type.dtdelta(datetime.timedelta())

    def test_path(self):
        """Simple test."""
        assert tools.is_type.path(tools.pathlib.Path("x"))


class TestStrip(object):
    """Test tools.strip."""

    def test_left_str(self):
        """Simple test."""
        x = "badwolfbadwolf"
        y = tools.strip.left(x, "badwolf")
        assert y == "badwolf"

    def test_left_list(self):
        """Simple test."""
        x = ["badwolfbadwolf", "badwolf", "abadwolfbadwolf"]
        y = tools.strip.left(x, "badwolf")
        assert y == ["badwolf", "", "abadwolfbadwolf"]

    def test_left_str_nomatch(self):
        """Simple test."""
        x = "abadwolfbadwolf"
        y = tools.strip.left(x, "badwolf")
        assert y == "abadwolfbadwolf"

    def test_right_str(self):
        """Simple test."""
        x = "badwolfbadwolf"
        y = tools.strip.right(x, "badwolf")
        assert y == "badwolf"

    def test_right_str_nomatch(self):
        """Simple test."""
        x = "badwolfbadwolfa"
        y = tools.strip.right(x, "badwolf")
        assert y == "badwolfbadwolfa"

    def test_right_list(self):
        """Simple test."""
        x = ["badwolfbadwolf", "badwolf", "badwolfbadwolfa"]
        y = tools.strip.right(x, "badwolf")
        assert y == ["badwolf", "", "badwolfbadwolfa"]


class TestJson(object):
    """Test tools.json."""

    def test_load(self):
        """Simple test."""
        x = "{}"
        y = tools.json.load(x)
        assert y == {}

    def test_load_error_false(self):
        """Simple test."""
        x = "xxx"
        y = tools.json.load(x, error=False)
        assert y == "xxx"

    def test_load_error_true(self):
        """Simple test."""
        x = "xxx"
        with pytest.raises(Exception):
            tools.json.load(x, error=True)

    def test_dump(self):
        """Simple test."""
        x = {"x": 2}
        y = tools.json.dump(x)
        assert y == '{\n  "x": 2\n}'

    def test_dump_error_false(self):
        """Simple test."""
        x = pytest
        y = tools.json.dump(x, error=False)
        assert y == pytest

    def test_dump_error_true(self):
        """Simple test."""
        x = pytest
        with pytest.raises(Exception):
            tools.json.dump(x, error=True)

    def test_re_load(self):
        """Simple test."""
        x = '{"x": 2}'
        y = tools.json.re_load(x)
        assert y == '{\n  "x": 2\n}'

    def test_re_load_error_false(self):
        """Simple test."""
        x = "{"
        y = tools.json.re_load(x, error=False)
        assert y == x

    def test_re_load_error_true(self):
        """Simple test."""
        x = "{"
        with pytest.raises(Exception):
            tools.json.re_load(x, error=True)


class TestDt(object):
    """Test tools.dt."""

    def test_minutes_ago_utc_str(self):
        """Simple test."""
        then = format(tools.dt.now() - datetime.timedelta(minutes=1))
        assert tools.dt.minutes_ago(then) == 1

    def test_minutes_ago_utc_dt(self):
        """Simple test."""
        then = tools.dt.now() - datetime.timedelta(minutes=1)
        assert tools.dt.minutes_ago(then) == 1

    def test_minutes_ago_utc_dt_naive(self):
        """Simple test."""
        then = tools.dt.now(None) - datetime.timedelta(minutes=1)
        assert tools.dt.minutes_ago(then) == 1

    def test_minutes_ago_utc_dtdelta(self):
        """Simple test."""
        then = datetime.timedelta(minutes=3)
        assert tools.dt.minutes_ago(then) == 3

    def test_minutes_ago_naive(self):
        """Simple test."""
        then = datetime.datetime.now() - datetime.timedelta(minutes=1)
        assert tools.dt.minutes_ago(format(then)) == 1

    def test_now(self):
        """Pass."""
        now = tools.dt.now()
        assert now.tzinfo

    def test_now_notz(self):
        """Pass."""
        now = tools.dt.now(tz=None)
        assert not now.tzinfo

    def test_now_delta(self):
        """Pass."""
        then = tools.dt.now(delta=datetime.timedelta(minutes=5))
        assert tools.dt.minutes_ago(then) == 5

    def test_parse_str(self):
        """Pass."""
        now = format(tools.dt.now())
        now = tools.dt.parse(now)
        assert tools.is_type.dt(now)

    def test_parse_dt(self):
        """Pass."""
        now = tools.dt.now()
        now = tools.dt.parse(now)
        assert tools.is_type.dt(now)

    def test_parse_dtdelta(self):
        """Pass."""
        now = datetime.timedelta(minutes=1)
        now = tools.dt.parse(now)
        assert tools.is_type.dt(now)

    def test_parse_list(self):
        """Pass."""
        now = [format(tools.dt.now())]
        now = tools.dt.parse(now)
        assert tools.is_type.list(now)
        assert [tools.is_type.dt(x) for x in now]

    def test_within_min_none(self):
        """Pass."""
        assert tools.dt.within_minutes(tools.dt.now(), None) is False

    def test_within_min_5(self):
        """Pass."""
        then = tools.dt.now(delta=datetime.timedelta(minutes=5))
        assert tools.dt.within_minutes(then, 5) is True


class TestCsv(object):
    """Test tools.csv."""

    def test_lod(self):
        """Pass."""
        x = [{"a": 1}]
        result = tools.csv.lod(x)
        expected = ['"a"\r\n1\r\n', '"a"\n1\n']
        assert result in expected

    def test_lod_headers(self):
        """Pass."""
        x = [{"a": 1}]
        headers = ["a"]
        result = tools.csv.lod(x, headers=headers)
        expected = ['"a"\r\n1\r\n', '"a"\n1\n']
        assert result in expected

    def test_lod_headers_extra(self):
        """Pass."""
        x = [{"a": 1}]
        headers = ["a", "b"]
        result = tools.csv.lod(x, headers=headers)
        expected = ['"a","b"\r\n1,""\r\n', '"a","b"\n1,""\n']
        assert result in expected

    def test_lod_fieldnames(self):
        """Pass."""
        x = [{"a": 1}]
        fieldnames = ["a"]
        result = tools.csv.lod(x, fieldnames=fieldnames)
        expected = ['"a"\r\n1\r\n', '"a"\n1\n']
        assert result in expected

    def test_lod_fieldnames_extra(self):
        """Pass."""
        x = [{"a": 1}]
        fieldnames = ["a", "b"]
        result = tools.csv.lod(x, fieldnames=fieldnames)
        expected = ['"a","b"\r\n1,""\r\n', '"a","b"\n1,""\n']
        assert result in expected

    def test_lod_fieldnames_extra_headers_ignored(self):
        """Pass."""
        x = [{"a": 1}]
        fieldnames = ["a", "b"]
        headers = ["a"]
        result = tools.csv.lod(x, headers=headers, fieldnames=fieldnames)
        expected = ['"a","b"\r\n1,""\r\n', '"a","b"\n1,""\n']
        assert result in expected

    def test_lod_custom_stream(self):
        """Pass."""
        stream = six.StringIO()
        x = [{"a": 1}]
        result = tools.csv.lod(x, stream=stream)
        expected = ['"a"\r\n1\r\n', '"a"\n1\n']
        assert result in expected

    def test_lod_stream_value_false(self):
        """Pass."""
        x = [{"a": 1}]
        result = tools.csv.lod(x, stream_value=False)
        expected = ['"a"\r\n1\r\n', '"a"\n1\n']
        assert isinstance(result, six.StringIO)
        assert result.getvalue() in expected

    def test_lod_compress(self):
        """Pass."""
        x = [{"a": 1}]
        result = tools.csv.lod(x, compress=True)
        expected = ['"a"\r\n"1"\r\n', '"a"\n"1"\n']
        assert result in expected

    def test_compress_dicts(self):
        """Pass."""
        x = [{"a": 1}]
        result = tools.csv.compress_dicts(x)
        expected = [{"a": "1"}]
        assert result == expected

    def test_compress_dicts_complex1(self):
        """Pass."""
        x = [{"a": {"b": 1}}]
        result = tools.csv.compress_dicts(x)
        expected = [{"a.b": "1"}]
        assert result == expected

    def test_compress_dicts_complex2(self):
        """Pass."""
        x = [{"a": {"b": [1, 2]}}]
        result = tools.csv.compress_dicts(x)
        expected = [{"a.b": "1\n2"}]
        assert result == expected

    def test_compress_dicts_complex3(self):
        """Pass."""
        x = [{"a": {"b": [[1], [2]]}}]
        result = tools.csv.compress_dicts(x)
        expected = [{"a.b": "1\n2"}]
        assert result == expected

    def test_compress_dicts_complex4(self):
        """Pass."""
        x = [{"a": {"b": [{"c": 1}, {"d": 2}]}}]
        result = tools.csv.compress_dicts(x)
        expected = [{"a.b.0.c": "1", "a.b.1.d": "2"}]
        assert result == expected

    def test_compress_dicts_complex5(self):
        """Pass."""
        x = [{"a": {"b": [{"c": [1, 2]}, {"d": [3, 4]}]}}]
        result = tools.csv.compress_dicts(x)
        expected = [{"a.b.0.c": "1\n2", "a.b.1.d": "3\n4"}]
        assert result == expected

    def test_compress_dicts_complex_unhandled(self):
        """Pass."""
        x = [{"a": {"b": [[{"c": 1}], [{"d": 2}]]}}]
        with pytest.raises(axonapi.exceptions.ToolsError):
            tools.csv.compress_dicts(x)


class TestLogs(object):
    """Test tools.logs."""

    def test_gmtime(self):
        """Pass."""
        tools.logs.gmtime()
        assert logging.Formatter.converter == time.gmtime

    def test_localtime(self):
        """Pass."""
        tools.logs.localtime()
        assert logging.Formatter.converter == time.localtime

    def test_get_obj_log(self):
        """Pass."""
        log = tools.logs.get_obj_log(self, "warning")
        assert log.name == "axonius_api_client.tests.test_tools.TestLogs"
        assert log.level == logging.WARNING

    def test_str_level_int(self):
        """Pass."""
        assert tools.logs.str_level(10) == "DEBUG"

    def test_str_level_str_int(self):
        """Pass."""
        assert tools.logs.str_level("10") == "DEBUG"

    def test_str_level_str(self):
        """Pass."""
        assert tools.logs.str_level("debug") == "DEBUG"

    def test_str_level_fail(self):
        """Pass."""
        with pytest.raises(axonapi.exceptions.ToolsError):
            tools.logs.str_level("xx")

    def test_add_del_stderr(self):
        """Pass."""
        h = tools.logs.add_stderr(tools.LOG)
        assert h.name == axonapi.constants.LOG_NAME_STDERR
        assert (
            tools.logs.str_level(h.level).lower() == axonapi.constants.LOG_LEVEL_CONSOLE
        )
        assert isinstance(h, logging.StreamHandler)
        assert h in tools.LOG.handlers

        dh = tools.logs.del_stderr(tools.LOG)
        assert tools.is_type.dict(dh)
        assert tools.LOG.name in dh
        assert tools.is_type.list(dh[tools.LOG.name])
        assert h in dh[tools.LOG.name]
        assert h not in tools.LOG.handlers

    def test_add_del_stdout(self):
        """Pass."""
        h = tools.logs.add_stdout(tools.LOG)
        assert h.name == axonapi.constants.LOG_NAME_STDOUT
        assert (
            tools.logs.str_level(h.level).lower() == axonapi.constants.LOG_LEVEL_CONSOLE
        )
        assert isinstance(h, logging.StreamHandler)
        assert h in tools.LOG.handlers

        dh = tools.logs.del_stdout(tools.LOG)
        assert tools.is_type.dict(dh)
        assert tools.LOG.name in dh
        assert tools.is_type.list(dh[tools.LOG.name])
        assert h in dh[tools.LOG.name]
        assert h not in tools.LOG.handlers

    def test_add_del_null(self):
        """Pass."""
        tools.logs.del_null(tools.LOG)
        h = tools.logs.add_null(tools.LOG)
        assert h.name == "NULL"
        assert isinstance(h, logging.NullHandler)
        assert h in tools.LOG.handlers

        fh = tools.logs.add_null(tools.LOG)
        assert fh is None

        dh = tools.logs.del_null(tools.LOG)

        assert tools.is_type.dict(dh)
        assert tools.is_type.list(dh[tools.LOG.name])

        assert tools.LOG.name in dh
        f = dh.pop(tools.LOG.name)

        assert h in f
        assert h not in tools.LOG.handlers
        assert not dh

    def test_add_del_file(self):
        """Pass."""
        h = tools.logs.add_file(tools.LOG)
        assert h.name == axonapi.constants.LOG_NAME_FILE
        assert tools.logs.str_level(h.level).lower() == axonapi.constants.LOG_LEVEL_FILE
        assert isinstance(h, tools.logging.handlers.RotatingFileHandler)
        assert h in tools.LOG.handlers
        assert getattr(h, "PATH", None)
        assert isinstance(h.PATH, tools.pathlib.Path)

        dh = tools.logs.del_file(tools.LOG)
        assert tools.is_type.dict(dh)
        assert tools.LOG.name in dh
        assert tools.is_type.list(dh[tools.LOG.name])
        assert h in dh[tools.LOG.name]
        assert h not in tools.LOG.handlers


@pytest.mark.needs_url
class TestConnect(object):
    """Pass."""

    def test_no_start(self, url):
        """Pass."""
        c = tools.Connect(url=url, key=BAD_CRED, secret=BAD_CRED)
        assert "Not connected" in format(c)
        assert "Not connected" in repr(c)
        assert c._handler_file is None
        assert c._handler_con is None

    def test_no_start_logs(self, url):
        """Pass."""
        c = tools.Connect(
            url=url, key=BAD_CRED, secret=BAD_CRED, log_console=True, log_file=True
        )
        assert "Not connected" in format(c)
        assert "Not connected" in repr(c)
        assert isinstance(c._handler_file, logging.Handler)
        assert isinstance(c._handler_con, logging.Handler)

    @pytest.mark.needs_key_creds
    def test_start(self, url, creds_key):
        """Pass."""
        c = tools.Connect(
            url=url,
            key=creds_key["creds"]["key"],
            secret=creds_key["creds"]["secret"],
            certwarn=False,
        )
        c.start()
        assert "Connected" in format(c)
        assert "Connected" in repr(c)

    def test_invalid_creds(self, url):
        """Pass."""
        c = tools.Connect(url=url, key=BAD_CRED, secret=BAD_CRED, certwarn=False)
        c._http._CONNECT_TIMEOUT = 1
        with pytest.raises(axonapi.exceptions.ConnectError) as exc:
            c.start()
        assert isinstance(exc.value.exc, axonapi.exceptions.InvalidCredentials)

    def test_connect_timeout(self):
        """Pass."""
        c = tools.Connect(
            url="127.0.0.99", key=BAD_CRED, secret=BAD_CRED, certwarn=False
        )
        c._http._CONNECT_TIMEOUT = 1
        with pytest.raises(axonapi.exceptions.ConnectError) as exc:
            c.start()
        assert isinstance(
            exc.value.exc, axonapi.http.requests.exceptions.ConnectTimeout
        )

    def test_connect_error(self):
        """Pass."""
        c = tools.Connect(
            url="https://127.0.0.1:3919", key=BAD_CRED, secret=BAD_CRED, certwarn=False
        )
        c._http._CONNECT_TIMEOUT = 1
        with pytest.raises(axonapi.exceptions.ConnectError) as exc:
            c.start()
        assert isinstance(
            exc.value.exc, axonapi.http.requests.exceptions.ConnectionError
        )

    def test_invalid_creds_nowrap(self, url):
        """Pass."""
        c = tools.Connect(
            url=url, key=BAD_CRED, secret=BAD_CRED, certwarn=False, wraperror=False
        )
        c._http._CONNECT_TIMEOUT = 1
        with pytest.raises(axonapi.exceptions.InvalidCredentials):
            c.start()

    def test_other_exc(self, url):
        """Pass."""
        c = tools.Connect(
            url="127.0.0.1", key=BAD_CRED, secret=BAD_CRED, certwarn=False
        )
        c._http._CONNECT_TIMEOUT = 1
        c._auth._creds = None
        with pytest.raises(axonapi.exceptions.ConnectError):
            c.start()

    def test_reason(self):
        """Pass."""
        exc = Exception("badwolf")
        reason = tools.Connect._get_exc_reason(exc)
        assert format(reason) == "badwolf"
