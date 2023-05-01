# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client."""
import codecs
import io
import tempfile
from datetime import timezone

import dateutil.tz
import pytest

from axonius_api_client.api.json_api.generic import IntValue
from axonius_api_client.constants.api import GUI_PAGE_SIZES
from axonius_api_client.constants.general import IS_WINDOWS
from axonius_api_client.exceptions import ToolsError
from axonius_api_client.tools import (
    bom_strip,
    calc_perc_gb,
    calc_percent,
    check_empty,
    check_gui_page_size,
    check_path_is_not_dir,
    check_type,
    coerce_bool,
    coerce_int,
    coerce_int_float,
    coerce_str,
    coerce_str_to_csv,
    combo_dicts,
    datetime,
    dt_days_left,
    dt_min_ago,
    dt_now,
    dt_now_file,
    dt_parse,
    dt_parse_tmpl,
    dt_within_min,
    echo_debug,
    echo_error,
    echo_ok,
    echo_warn,
    get_backup_filename,
    get_backup_path,
    get_cls_path,
    get_path,
    get_paths_format,
    get_raw_version,
    get_type_str,
    grouper,
    is_email,
    is_int,
    is_str,
    is_url,
    join_kv,
    join_url,
    json_dump,
    json_load,
    json_reload,
    kv_dump,
    listify,
    longest_str,
    parse_int_min_max,
    parse_ip_address,
    parse_ip_network,
    path_backup_file,
    path_create_parent_dir,
    path_read,
    path_write,
    pathlib,
    prettify_obj,
    read_stream,
    split_str,
    strip_left,
    strip_right,
    strip_str,
    sysinfo,
    token_parse,
)

BOM_BYTES = codecs.BOM_UTF8
BOM_STR = BOM_BYTES.decode()


class TestIsStr:
    def test_true(self):
        assert is_str(value="xxx") is True

    def test_empty(self):
        assert is_str(value="") is False

    def test_false(self):
        assert is_str(value=111) is False


class TestIsEmail:
    def test_true(self):
        assert is_email(value="jim@axonius.com") is True

    def test_false(self):
        assert is_email(value="xxx") is False


class TestCoerceStr:
    @pytest.mark.parametrize(
        "value,exp",
        [
            [b"", ""],
            [" x ", "x"],
            [None, ""],
            [2, "2"],
        ],
    )
    def test_valids(self, value, exp):
        assert coerce_str(value=value) == exp

    def test_trim(self):
        value = " xxxxxx "
        exp = "xxxx\n"
        assert coerce_str(value=value, trim=4).startswith(exp)

    def test_trim_lines(self):
        value = "\n".join(["1", "2", "3"])
        exp = "1\n2\nTrimmed 3 lines down to 2"
        ret = coerce_str(value=value, trim=2, trim_lines=2)
        assert ret == exp


class TestDtDaysLeft:
    def test_valid(self):
        assert dt_days_left(datetime.datetime.utcnow() + datetime.timedelta(days=100)) == 100


class TestKvDump:
    def test_valid(self):
        assert kv_dump({"k": "v", "a": "b"}) == "\n  k: v\n  a: b"


class TestBomStrip:
    def test__str(self):
        assert bom_strip(content=f" {BOM_STR}test") == "test"

    def test_bytes(self):
        assert bom_strip(content=b" " + BOM_BYTES + b"test") == b"test"


class TestPrettifyObj:
    @pytest.mark.parametrize(
        "value,exp",
        [
            [{}, ["", "-----"]],
            [{"str": "foo"}, ["", "-----", "- str:", "   foo"]],
            [{"list_str": ["foo1", "foo2"]}, ["", "-----", "- list_str:", "   foo1", "   foo2"]],
        ],
    )
    def test_valids(self, value, exp):
        assert prettify_obj(value) == exp


class TestParseIntMinMax:
    def test_str_int(self):
        ret = parse_int_min_max(value="4", default=0)
        assert ret == 4

    def test_int(self):
        ret = parse_int_min_max(value=4, default=0)
        assert ret == 4

    def test_str_non_int(self):
        ret = parse_int_min_max(value="x", default=0)
        assert ret == 0

    def test_min_fallback(self):
        ret = parse_int_min_max(value="4", default=0, min_value=5)
        assert ret == 0

    def test_max_fallback(self):
        ret = parse_int_min_max(value="4", default=0, max_value=3)
        assert ret == 0


class TestGetBackupPath:
    def test_valid(self, tmp_path):
        path = tmp_path / "exergy.txt"
        ret = get_backup_path(str(path))
        parts = ret.stem.split("_")[1].split("-")
        assert [x.isdigit() for x in parts]


class TestGetClsPath:
    def test_cls(self):
        class Fun:
            pass

        exp = "axonius_api_client.tests.tests_pkg.test_tools.Fun"
        ret = get_cls_path(value=Fun)
        assert ret == exp

    def test_obj(self):
        class Fun:
            pass

        exp = "axonius_api_client.tests.tests_pkg.test_tools.Fun"
        ret = get_cls_path(value=Fun())
        assert ret == exp


class TestGetBackupFilename:
    def test_valid(self, tmp_path):
        path = tmp_path / "exergy.txt"
        ret = get_backup_filename(str(path))
        parts = ret.split(".")[0].split("_")[1].split("-")
        assert [x.isdigit() for x in parts]


class TestCheckPathIsNotDir:
    def test_valid(self, tmp_path):
        path = tmp_path / "oh_hai.txt"
        path.touch()
        ret = check_path_is_not_dir(path=str(path))
        assert ret == path

    def test_invalid(self, tmp_path):
        path = tmp_path / "oh_hai"
        path.mkdir()
        with pytest.raises(ToolsError):
            check_path_is_not_dir(path=str(path))


class TestPathCreateParentDir:
    def test_valid(self, tmp_path):
        path = tmp_path / "d1" / "d2" / "file.txt"
        ret = path_create_parent_dir(path=path)
        assert ret.parent.is_dir()

    def test_invalid(self, tmp_path):
        path = tmp_path / "d1" / "d2" / "file.txt"
        with pytest.raises(ToolsError):
            path_create_parent_dir(path=path, make_parent=False)
        assert not path.parent.is_dir()


class TestPathBackupFile:
    def test_not_exists(self, tmp_path):
        path = tmp_path / "file.txt"
        with pytest.raises(ToolsError):
            path_backup_file(path=path)

    def test_backup_path_isdir(self, tmp_path):
        path = tmp_path / "file.txt"
        path.touch()
        backup_path = tmp_path / "backup"
        backup_path.mkdir()
        with pytest.raises(ToolsError):
            path_backup_file(path=path, backup_path=backup_path)

    def test_backup_path_exists(self, tmp_path):
        path = tmp_path / "d1" / "file.txt"
        path.parent.mkdir()
        path.touch()
        backup_path = tmp_path / "d2" / "backup.txt"
        backup_path.parent.mkdir()
        backup_path.touch()
        ret = path_backup_file(path=path, backup_path=backup_path)
        assert ret.name != backup_path.name
        assert ret.parent == backup_path.parent


class TestTokenParse:
    @pytest.mark.parametrize("value,exp", [["token=sadpanda", "sadpanda"], ["boo", "boo"]])
    def test_valids(self, value, exp):
        assert token_parse(value) == exp


class TestStripStr:
    @pytest.mark.parametrize("value,exp", [[" boo ", "boo"], ["boo", "boo"], [1, 1]])
    def test_valids(self, value, exp):
        assert strip_str(value) == exp


class TestIsUrl:
    @pytest.mark.parametrize("value,exp", [["https://blah.com", True], ["blah.com", False]])
    def test_valids(self, value, exp):
        assert is_url(value) == exp


class TestComboDicts:
    def test_valid(self):
        d1 = {1: 2}
        d2 = {3: 4}
        d3 = {5: 6}
        d4 = {1: 4}
        exp = {1: 4, 3: 4, 5: 6}
        ret = combo_dicts(d1, d2, d3, d4)
        assert ret == exp


class TestCalcPercGb:
    def test_valid(self):
        obj = {"available": 200000, "total": 500000}
        exp = {
            "available": 200000,
            "total": 500000,
            "available_gb": 0.19,
            "total_gb": 0.48,
            "available_percent": 39.58,
        }
        ret = calc_perc_gb(obj=obj, whole_key="total", part_key="available")
        assert ret == exp


class TestCheckGuiPageSize:
    def test_invalid(self):
        with pytest.raises(ToolsError):
            check_gui_page_size(size=9999)

    def test_valid(self):
        assert check_gui_page_size(size=f"{GUI_PAGE_SIZES[0]}") == GUI_PAGE_SIZES[0]


class TestEchos:
    def test_ok(self, capsys):
        entry = "xxxxxxx"
        echo_ok(msg=entry)
        capture = capsys.readouterr()
        assert entry in capture.err
        assert not capture.out

    def test_debug(self, capsys):
        entry = "xxxxxxx"
        echo_debug(msg=entry)
        capture = capsys.readouterr()
        assert entry in capture.err
        assert not capture.out

    def test_warning(self, capsys):
        entry = "xxxxxxx"
        echo_warn(msg=entry)
        capture = capsys.readouterr()
        assert entry in capture.err
        assert not capture.out

    def test_error_no_abort(self, capsys):
        entry = "xxxxxxx"
        echo_error(msg=entry, abort=False)
        capture = capsys.readouterr()
        assert entry in capture.err
        assert not capture.out

    def test_error(self, capsys):
        entry = "xxxxxxx"
        with pytest.raises(SystemExit):
            echo_error(msg=entry)


class TestReadStream:
    def test_valid(self):
        ret = read_stream(io.StringIO("xx"))
        assert ret == "xx"

    def test_empty_fd(self):
        with pytest.raises(ToolsError):
            read_stream(io.StringIO())

    def test_empty_stdin(self, monkeypatch):
        stream = io.StringIO()
        monkeypatch.setattr(stream, "isatty", lambda: True)
        with pytest.raises(ToolsError):
            read_stream(stream)


class TestCoerceBool:
    def test_invalid(self):
        with pytest.raises(ToolsError):
            coerce_bool("badwolf")

    @pytest.mark.parametrize(
        "value,exp",
        [
            ["y", True],
            ["yes", True],
            ["true", True],
            ["True", True],
            ["1", True],
            [1, True],
            ["t", True],
            [True, True],
            ["n", False],
            ["no", False],
            ["false", False],
            ["False", False],
            ["0", False],
            [0, False],
            ["f", False],
            [False, False],
        ],
    )
    def test_valids(self, value, exp):
        assert coerce_bool(value) == exp


class TestCoerceIntFloat:
    def test_invalid(self):
        with pytest.raises(ToolsError):
            coerce_int_float("1.x")

    @pytest.mark.parametrize(
        "value,exp",
        [
            [1.0, 1.0],
            [1, 1],
            ["1", 1],
            ["1.0", 1.0],
        ],
    )
    def test_valids(self, value, exp):
        assert coerce_int_float(value) == exp


class TestCoerceInt:
    def test_invalid_str(self):
        with pytest.raises(ToolsError):
            coerce_int("badwolf")

    def test_valid_str(self):
        assert coerce_int("456") == 456

    def test_min(self):
        with pytest.raises(ToolsError):
            coerce_int(obj=2, min_value=3)

    def test_max(self):
        with pytest.raises(ToolsError):
            coerce_int(obj=2, max_value=1)

    def test_min_max(self):
        with pytest.raises(ToolsError):
            coerce_int(obj=2, min_value=3, max_value=1)

    def test_invalid_value(self):
        with pytest.raises(ToolsError):
            coerce_int(obj=2, valid_values=[1, 3])

    def test_valid(self):
        ret = coerce_int(obj="1", valid_values=[1, 3])
        assert ret == 1


class TestJoinUrl:
    """Test axonius_api_client.join_url."""

    @pytest.mark.parametrize(
        "value,exp",
        [
            [("https://test.com",), "https://test.com/"],
            [("https://test.com/",), "https://test.com/"],
            [("https://test.com////",), "https://test.com/"],
            [
                (
                    "https://test.com",
                    "",
                ),
                "https://test.com/",
            ],
            [
                (
                    "https://test.com",
                    "",
                    "",
                ),
                "https://test.com/",
            ],
            [
                (
                    "https://test.com",
                    "/",
                    "",
                ),
                "https://test.com/",
            ],
            [
                (
                    "https://test.com",
                    "/",
                    "/",
                ),
                "https://test.com/",
            ],
        ],
    )
    def test_url(self, value, exp):
        """Test url gets joined properly no matter the slashes."""
        assert join_url(*value) == exp

    @pytest.mark.parametrize(
        "value,exp",
        [
            [
                (
                    "https://test.com",
                    "a",
                ),
                "https://test.com/a",
            ],
            [
                (
                    "https://test.com",
                    "/a",
                ),
                "https://test.com/a",
            ],
            [
                (
                    "https://test.com",
                    "//a",
                ),
                "https://test.com/a",
            ],
            [
                (
                    "https://test.com",
                    "a/",
                ),
                "https://test.com/a/",
            ],
            [
                (
                    "https://test.com",
                    "a/b",
                ),
                "https://test.com/a/b",
            ],
            [
                (
                    "https://test.com",
                    "a/b",
                    "",
                ),
                "https://test.com/a/b",
            ],
            [
                (
                    "https://test.com",
                    "a/b/",
                    "",
                ),
                "https://test.com/a/b/",
            ],
            [
                (
                    "https://test.com",
                    "a/b",
                    "/",
                ),
                "https://test.com/a/b/",
            ],
            [
                (
                    "https://test.com",
                    "a/b",
                    "/////",
                ),
                "https://test.com/a/b/",
            ],
        ],
    )
    def test_url_path(self, value, exp):
        """Test url, path gets joined properly no matter the slashes."""
        assert join_url(*value) == exp

    @pytest.mark.parametrize(
        "value,exp",
        [
            [
                (
                    "https://test.com",
                    "a",
                    "b",
                ),
                "https://test.com/a/b",
            ],
            [
                (
                    "https://test.com",
                    "/a",
                    "b",
                ),
                "https://test.com/a/b",
            ],
            [
                (
                    "https://test.com",
                    "//a",
                    "b",
                ),
                "https://test.com/a/b",
            ],
            [
                (
                    "https://test.com",
                    "a",
                    "b/c/d",
                ),
                "https://test.com/a/b/c/d",
            ],
        ],
    )
    def test_url_path_route(self, value, exp):
        """Test url, path, route gets joined properly no matter the slashes."""
        assert join_url(*value) == exp


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
        ret_path, ret_info = path_write(obj=path, data=data)
        ret_write, ret_backup = ret_info
        assert ret_path.read_text() == data
        assert format(ret_path) == format(path)
        assert ret_write == len(data)
        assert ret_backup is None
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
        ret_path, ret_info = path_write(obj=format(path), data=data)
        ret_write, ret_backup = ret_info
        assert ret_path.read_text() == data
        assert format(ret_path) == format(path)
        assert ret_write == len(data)
        assert ret_backup is None

    def test_parent_fail(self, tmp_path):
        """Test simple write with pathlib object."""
        sub1 = tmp_path / "sub1"
        sub2 = sub1 / "sub2"
        path = sub2 / "file.txt"
        data = "abc\n123\n"
        with pytest.raises(ToolsError):
            path_write(obj=path, data=data, make_parent=False)

    def test_noperm_parent(self):
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

    def test_dump_bytes(self):
        """Simple test."""
        x = b"xxx"
        y = json_dump(obj=x)
        assert y == '"xxx"'

    def test_serial(self):
        dc = IntValue(value=1111)
        now = datetime.datetime.utcnow()
        obj = {"foo": json_dump, "now": now, "dc": dc}

        exp = [
            "{",
            f'  "foo": "{json_dump}",',
            f'  "now": "{now.isoformat()}",',
            '  "dc": {',
            '    "value": 1111,',
            '    "document_meta": {}',
            "  }",
            "}",
        ]

        ret = json_dump(obj)
        assert ret.splitlines() == exp

    def test_hasdict(self):
        class Moofasa:
            def to_dict(self):
                return {"x": "v"}

        obj = Moofasa()
        exp = ["{", '  "x": "v"', "}"]

        ret = json_dump(obj)
        assert ret.splitlines() == exp


class TestDtParseTmpl:
    def test_valid(self):
        assert dt_parse_tmpl("2019-07-09T09:22:21") == "2019-07-09"
        assert dt_parse_tmpl("20190709T09:22:21") == "2019-07-09"

    def test_invalid(self):
        with pytest.raises(ToolsError):
            dt_parse_tmpl("2019-07-09Txx")
        with pytest.raises(ToolsError):
            dt_parse_tmpl("xxx")


class TestDtNowFile:
    def test_valid(self):
        ret = dt_now_file()
        assert isinstance(ret, str) and ret


class TestSplitStr:
    def test_valid(self):
        assert split_str("x, y, z") == ["x", "y", "z"]
        assert split_str(["x, y, z", "a, b, c"]) == ["x", "y", "z", "a", "b", "c"]
        assert split_str(None) == []
        assert split_str(["x,,y,,z"]) == ["x", "y", "z"]

    def test_invalid(self):
        with pytest.raises(ToolsError):
            split_str({})


class TestLongestStr:
    def test_valid(self):
        assert longest_str(["a" * 5, "b" * 20, "c" * 3]) == 20


class TestSysInfo:
    def test_valid(self):
        data = sysinfo()
        assert isinstance(data, dict)


class TestCalc:
    def test_valid(self):
        assert calc_percent(0, 100) == 0.00
        assert calc_percent(50, 57) == 87.72
        assert calc_percent(50, 57, 0) == 88
        assert calc_percent(59, 57) == 100.00


class TestJoinKv:
    def test_valid(self):
        assert join_kv({"k1": "v1", "k2": "v2"}) == ["k1: 'v1'", "k2: 'v2'"]
        assert join_kv([{"k1": "v1"}, {"k2": "v2"}]) == [["k1: 'v1'"], ["k2: 'v2'"]]
        assert join_kv({"k1": ["v1", "v2"]}) == ["k1: 'v1, v2'"]

    def test_invalid(self):
        with pytest.raises(ToolsError):
            join_kv(2)


class TestChecks:
    def test_get_type_str(self):
        assert get_type_str(list) == "list"
        assert get_type_str((list, dict)) == "list or dict"

    def test_check_type_valid(self):
        check_type([], exp=list)
        check_type(["x", 1], exp=list, exp_items=(str, int))

    def test_check_type_invalid(self):
        with pytest.raises(ToolsError):
            check_type([], exp=dict)

        with pytest.raises(ToolsError):
            check_type(["x", 1], exp=list, exp_items=str)

    def test_check_empty_valid(self):
        check_empty(["x"])

    def test_check_empty_invalid(self):
        with pytest.raises(ToolsError):
            check_empty([])


class TestGetRawVersion:
    def test_valid(self):
        assert get_raw_version("3.1.0") == "0000000030000000100000000"
        assert get_raw_version("boo:2.1.0") == "boo000000020000000100000000"
        assert get_raw_version("123456789123456789.1.0") == "0123456780000000100000000"

    def test_invalid(self):
        with pytest.raises(ToolsError):
            get_raw_version("3.1.0:x")

        with pytest.raises(ToolsError):
            get_raw_version("3.x.0")


class TestParseIpAddress:
    def test_valid(self):
        assert str(parse_ip_address("127.0.0.1")) == "127.0.0.1"

    def test_invalid(self):
        with pytest.raises(ToolsError):
            parse_ip_address("127.0.0")


class TestParseIpNetwork:
    def test_valid(self):
        assert str(parse_ip_network("127.0.0.1/32")) == "127.0.0.1/32"

    def test_invalid(self):
        with pytest.raises(ToolsError):
            parse_ip_network("127.0.0.1")

        with pytest.raises(ToolsError):
            parse_ip_network("127.0.0/32")


class TestCoerceStrToCsv:
    def test_valid(self):
        assert coerce_str_to_csv("x, y,, z") == ["x", "y", "z"]

    def test_invalid(self):
        with pytest.raises(ToolsError):
            coerce_str_to_csv({})

        with pytest.raises(ToolsError):
            coerce_str_to_csv(",,,")

        with pytest.raises(ToolsError):
            coerce_str_to_csv("")

        with pytest.raises(ToolsError):
            coerce_str_to_csv([])


class TestJsonReload:
    """Test json_dump."""

    def test_re_load(self):
        """Simple test."""
        x = '{"x": 2}'
        y = json_reload(obj=x)
        assert y == '{\n  "x": 2\n}'

    def test_re_load_trim(self):
        """Simple test."""
        obj = '{"x": "{aaaaaaaaaaaaaaaaaaaaaaaaa}"}'
        exp = '{\n  "x": "{aaaaaaaaa\nTrimmed 40 characters down to 20'
        ret = json_reload(obj=obj, trim=20)
        assert ret == exp

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
        then = format(dt_now() - datetime.timedelta(minutes=1))
        assert dt_min_ago(obj=then) == 1

    def test_min_ago_utc_dt(self):
        """Simple test."""
        then = dt_now() - datetime.timedelta(minutes=1)
        assert dt_min_ago(obj=then) == 1

    def test_min_ago_utc_dt_naive(self):
        """Simple test."""
        then = dt_now(None) - datetime.timedelta(minutes=1)
        assert dt_min_ago(obj=then) == 1

    def test_min_ago_utc_dtdelta(self):
        """Simple test."""
        then = datetime.timedelta(minutes=3)
        assert dt_min_ago(obj=then) == 3

    def test_min_ago_naive(self):
        """Simple test."""
        then = datetime.datetime.now() - datetime.timedelta(minutes=1)
        assert dt_min_ago(obj=format(then)) == 1


class TestDtNow:
    """Test dt_*."""

    def test_now(self):
        now = dt_now()
        assert now.tzinfo

    def test_now_notz(self):
        now = dt_now(tz=None)
        assert not now.tzinfo

    def test_now_delta(self):
        then = dt_now(delta=datetime.timedelta(minutes=5))
        assert dt_min_ago(then) == 5


class TestDtParse:
    """Test dt_*."""

    @pytest.mark.parametrize(
        "val",
        [format(dt_now()), dt_now(), datetime.timedelta(minutes=1)],
        scope="class",
    )
    def test_val(self, val):
        now = dt_parse(obj=val)
        assert isinstance(now, datetime.datetime)

    def test_list(self):
        now = [format(dt_now())]
        now = dt_parse(obj=now)
        assert isinstance(now, list)
        assert [isinstance(x, datetime.datetime) for x in now]

    def test_default_tz(self):
        now = datetime.datetime.now()
        assert not now.tzinfo
        ret = dt_parse(obj=now, default_tz_utc=True)
        assert ret.tzinfo in [dateutil.tz.tzutc(), timezone.utc]


class TestDtWithinMin:
    """Test dt_*."""

    @pytest.mark.parametrize("val", [None, "x", False, True, {}, [], 6, "8", b"9"], scope="class")
    def test_bad(self, val):
        then = dt_now(delta=datetime.timedelta(minutes=5))
        assert dt_within_min(obj=then, n=val) is False

    @pytest.mark.parametrize("val", [0, 4, "1", b"2"], scope="class")
    def test_ok(self, val):
        then = dt_now(delta=datetime.timedelta(minutes=5))
        assert dt_within_min(obj=then, n=val) is True


class TestGetPathsFormat:
    def test_basic(self):
        exp = pathlib.Path("/x")
        ret = get_paths_format("/x")
        assert exp == ret

    def test_basic2(self):
        exp = pathlib.Path("/x/y/z")
        ret = get_paths_format("/x", "y", "z")
        assert exp == ret

    def test_abs_overwrite(self):
        exp = pathlib.Path("/z")
        ret = get_paths_format("/x", "y", "/z")
        assert exp == ret

    def test_mapping_miss(self):
        exp = pathlib.Path("/x/{DATE}/z")
        ret = get_paths_format("/x", "{DATE}", "z", mapping={"NOPE": "xxx"})
        assert exp == ret

    def test_mapping_hit(self):
        exp = pathlib.Path("/x/xxx/z/ddd_xxx.txt")
        ret = get_paths_format("/x", "{DATE}", "z", "ddd_{DATE}.txt", mapping={"{DATE}": "xxx"})
        assert exp == ret
