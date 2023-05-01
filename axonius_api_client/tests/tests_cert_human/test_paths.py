# -*- coding: utf-8 -*-
"""Test suite."""
import datetime

import pytest

from axonius_api_client.projects.cert_human import paths


class TestFileInfo:
    def test_missing(self, tmp_path):
        tmp_path.mkdir(exist_ok=True)
        path = tmp_path / "file.txt"
        finfo = paths.FileInfo(path=path)
        assert str(finfo)
        assert repr(finfo)
        assert finfo.exists is False
        assert finfo.modified_days is None
        assert finfo.modified_delta is None
        assert finfo.modified_dt is None
        assert finfo.is_modified_days_ago(value=2) is None

    def test_exists(self, tmp_path):
        tmp_path.mkdir(exist_ok=True)
        path = tmp_path / "file.txt"
        path.touch()
        finfo = paths.FileInfo(path=path)
        assert str(finfo)
        assert repr(finfo)
        assert finfo.exists is True
        assert finfo.modified_days == 0
        assert isinstance(finfo.modified_delta, datetime.timedelta)
        assert isinstance(finfo.modified_dt, datetime.datetime)
        assert finfo.is_modified_days_ago(value=2) is False
        assert finfo.is_modified_days_ago(value=0) is True


class TestOctify:
    @pytest.mark.parametrize(
        "value, exp",
        (
            ("0700", (448, "0o700")),
            ("700", (448, "0o700")),
            ("0o700", (448, "0o700")),
            (444, (444, "0o674")),
        ),
    )
    def test_valids(self, value, exp):
        data = paths.octify(value=value)
        assert data == exp

    def test_allow_empty_true(self):
        data = paths.octify(value=None, allow_empty=True)
        assert data == (None, None)

    def test_allow_empty_False(self):
        with pytest.raises(ValueError):
            paths.octify(value=None, allow_empty=False)

    def test_bad_type(self):
        with pytest.raises(TypeError):
            paths.octify(value=[])

    def test_bad_length(self):
        with pytest.raises(ValueError):
            paths.octify(value=12345)

    def test_bad_str_int(self):
        with pytest.raises(ValueError):
            paths.octify(value="x")

    def test_error_false(self):
        exp = (None, None)
        data = paths.octify(value="x", error=False)
        assert data == exp


class TestIsExistingFile:
    def test_str_exists(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        path.touch()
        data = paths.is_existing_file(path=str(path))
        assert data is True

    def test_str_not_exists(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        data = paths.is_existing_file(path=str(path))
        assert data is False

    def test_str_multiline(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        path.touch()
        data = paths.is_existing_file(path=f"{path}\n")
        assert data is True

    def test_path_not_exists(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        data = paths.is_existing_file(path=path)
        assert data is False

    def test_path_exists(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        path.touch()
        data = paths.is_existing_file(path=path)
        assert data is True


class TestReadBytes:
    def test_exists(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        path.touch()
        content = b"xxxx"
        path.write_bytes(content)
        rpath, data = paths.read_bytes(path=str(path), exts=[".txt"])
        assert rpath == path
        assert data == content


class TestWriteBytes:
    def test_exists(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        content = b"xxxx"
        rpath = paths.write_bytes(path=path, content=content)
        assert rpath == path
        assert path.is_file()
        assert path.read_bytes() == content


class TestCreateFile:
    def test_overwrite_false(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        path.touch()
        with pytest.raises(paths.PathError):
            paths.create_file(path=path, overwrite=False)

    def test_overwrite_true(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        path.touch()
        rpath = paths.create_file(path=path, overwrite=True)
        assert rpath == path

    def test_overwrite_false_error_false(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        path.touch()
        rpath = paths.create_file(path=path, overwrite=False, error=False)
        assert rpath == path

    def test_not_exists(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        rpath = paths.create_file(path=path)
        assert rpath == path
        assert rpath.is_file()

    def test_make_parent_false(self, tmp_path):
        path = tmp_path / "badwolf" / "badwolf.txt"
        with pytest.raises(paths.PathNotFoundError):
            paths.create_file(path=path, make_parent=False)

    def test_make_parent_true(self, tmp_path):
        path = tmp_path / "badwolf" / "badwolf.txt"
        rpath = paths.create_file(path=path, make_parent=True)
        assert rpath.is_file()
        assert rpath.parent.is_dir()


class TestPathify:
    def test_str(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        path.touch()
        data = paths.pathify(path=str(path))
        assert data == path

    def test_bytes(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        path.touch()
        data = paths.pathify(path=str(path).encode("utf-8"))
        assert data == path

    def test_path(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        path.touch()
        data = paths.pathify(path=path)
        assert data == path

    def test_path_as_file(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        with pytest.raises(paths.PathNotFoundError):
            paths.pathify(path=path, as_file=True)
        path.touch()
        rpath = paths.pathify(path=path, as_file=True)
        assert path == rpath

    def test_path_as_dir(self, tmp_path):
        path = tmp_path / "badwolf"
        with pytest.raises(paths.PathNotFoundError):
            paths.pathify(path=path, as_dir=True)
        path.mkdir()
        rpath = paths.pathify(path=path, as_dir=True)
        assert path == rpath

    def test_path_exts(self, tmp_path):
        path = tmp_path / "badwolf.txt"
        with pytest.raises(paths.PathError):
            paths.pathify(path=path, exts=[".csv"])

        rpath = paths.pathify(path=path, exts=[".txt"])
        assert path == rpath


class TestFindFileExts:
    def test_success(self, tmp_path):
        files = ["test1.txt", "test2.txt", "test3.csv"]
        path = tmp_path / "test"
        path.mkdir()
        for x in files:
            (path / x).touch()

        exp = ["test1.txt", "test2.txt"]
        rpath, data = paths.find_file_exts(path=str(path), exts=[".txt"])
        names = [x.name for x in data]
        assert rpath == path
        assert names == exp

    def test_error_true_no_matches(self, tmp_path):
        files = ["test1.txt", "test2.txt", "test3.csv"]
        path = tmp_path / "test"
        path.mkdir()
        for x in files:
            (path / x).touch()

        with pytest.raises(paths.PathNotFoundError):
            paths.find_file_exts(path=str(path), exts=[".xml"], error=True)

    def test_error_false_no_matches(self, tmp_path):
        files = ["test1.txt", "test2.txt", "test3.csv"]
        path = tmp_path / "test"
        path.mkdir()
        for x in files:
            (path / x).touch()

        rpath, data = paths.find_file_exts(path=str(path), exts=[".xml"], error=False)
        assert rpath == path
        assert data == []

    def test_error_true_dir_not_exist(self, tmp_path):
        path = tmp_path / "test"
        with pytest.raises(paths.PathNotFoundError):
            paths.find_file_exts(path=str(path), exts=[".txt"], error=True)

    def test_error_false_dir_not_exist(self, tmp_path):
        path = tmp_path / "test"
        rpath, data = paths.find_file_exts(path=str(path), exts=[".txt"], error=False)
        assert rpath == path
        assert data == []
