# -*- coding: utf-8 -*-
"""Test suite."""
import datetime
import json

from axonius_api_client.cert_human import all_logs_list, ct_logs

FALLBACK = json.loads(all_logs_list.FALLBACK_JSON)


def check_data(data):
    assert isinstance(data, dict) and data
    assert isinstance(data["operators"], list) and data["operators"]
    for item in data["operators"]:
        assert isinstance(item, dict) and item


class TestLoadCtLogs:
    def test_success(self):
        data = ct_logs.load_ct_logs()
        check_data(data)

    def test_refetch(self, tmp_path):
        path = tmp_path / "i_do_not_exist.json"
        data = ct_logs.load_ct_logs(path=path)
        check_data(data)
        assert path.is_file()

    def test_fallback(self, tmp_path):
        path = tmp_path / "i_am_directory"
        path.mkdir()
        data = ct_logs.load_ct_logs(path=path, url="192.168.1.100", timeout=0.1)
        check_data(data)


class TestReadData:
    def test_success(self, tmp_path):
        path = tmp_path / "success.json"
        path.write_text(all_logs_list.FALLBACK_JSON)
        data = ct_logs.read_data(path=path)
        check_data(data)

    def test_not_exists(self, tmp_path):
        path = tmp_path / "i_do_not_exist.json"
        data = ct_logs.read_data(path=str(path))
        assert data is None

    def test_bad_json(self, tmp_path):
        path = tmp_path / "i_have_bad_json.json"
        path.write_bytes(b"][\n")
        data = ct_logs.read_data(path=path)
        assert data is None

    def test_fallback(self):
        data = ct_logs.read_data_fallback()
        check_data(data)


class TestRefetchData:
    def test_success(self):
        data = ct_logs.refetch_data()
        check_data(data)

    def test_fail(self):
        data = ct_logs.refetch_data(url="192.168.1.200", timeout=0.1)
        assert data is None


class TestWriteData:
    def test_success(self, tmp_path):
        path = tmp_path / "badwolf.json"
        ret = ct_logs.write_data(path=path, data=FALLBACK)
        assert ret is True
        assert path.is_file()

    def test_bad_type(self, tmp_path):
        path = tmp_path / "badwolf.json"
        ret = ct_logs.write_data(path=path, data=None)
        assert ret is False
        assert not path.is_file()

    def test_bad_path(self, tmp_path):
        path = tmp_path / "badwolf"
        path.mkdir(parents=True)
        ret = ct_logs.write_data(path=path, data=FALLBACK)
        assert ret is False
        assert not path.is_file()


class TestCalcRefetch:
    def test_calc_refetch_exists(self, tmp_path):
        path = tmp_path / "badwolf.json"
        path.touch()
        finfo = ct_logs.FileInfo(path=path)

        assert str(finfo)
        assert repr(finfo)
        assert finfo.exists
        assert isinstance(finfo.modified_dt, datetime.datetime)
        assert isinstance(finfo.modified_delta, datetime.timedelta)
        assert isinstance(finfo.modified_days, int)

        refetch = ct_logs.calc_refetch(path=path)
        assert refetch is False

    def test_calc_refetch_not_exists(self, tmp_path):
        path = tmp_path / "badwolf.json"
        finfo = ct_logs.FileInfo(path=path)

        assert str(finfo)
        assert repr(finfo)
        assert finfo.exists is False
        assert finfo.modified_dt is None
        assert finfo.modified_delta is None
        assert finfo.modified_days is None

        refetch = ct_logs.calc_refetch(path=path)
        assert refetch is True

    def test_calc_refetch_exists_past_max_days(self, tmp_path):
        path = tmp_path / "badwolf.json"
        path.touch()
        finfo = ct_logs.FileInfo(path=path)

        assert str(finfo)
        assert repr(finfo)
        assert finfo.exists is True
        assert isinstance(finfo.modified_dt, datetime.datetime)
        assert isinstance(finfo.modified_delta, datetime.timedelta)
        assert isinstance(finfo.modified_days, int)

        refetch = ct_logs.calc_refetch(path=path, modified_days_max=-1)
        assert refetch is True
