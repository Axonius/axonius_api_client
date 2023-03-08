# -*- coding: utf-8 -*-
"""Test suite."""
import typing as t

import pytest

from axonius_api_client.constants.fields import AXID
from axonius_api_client.exceptions import GrabberError
from axonius_api_client.parsers.grabber import Grabber, Hunter
from axonius_api_client.tools import csv_writer, json_dump

from ...utils import random_strs

CNT: int = 3
COL: str = AXID.name


def fake_ids(
    cnt: int = CNT, col: str = COL, length: int = 32, other: t.Optional[t.List[dict]] = None
) -> t.List[dict]:
    return [{col: x} for x in random_strs(num=cnt, length=length)] + (other or [])


def fake_json(cnt: int = CNT, col: str = COL, other: t.Optional[t.List[dict]] = None) -> str:
    return json_dump(fake_ids(cnt=cnt, col=col, other=other))


def fake_jsonl(cnt: int = CNT, col: str = COL, other: t.Optional[t.List[dict]] = None) -> str:
    return "\n".join([json_dump(x, indent=None) for x in fake_ids(cnt=cnt, col=col, other=other)])


def fake_csv(cnt: int = CNT, col: str = COL, other: t.Optional[t.List[dict]] = None) -> str:
    return csv_writer(rows=fake_ids(cnt=cnt, col=col, other=other))


class TestGrabber:
    def test_err_no_items_supplied(self):
        with pytest.raises(GrabberError, match=Grabber._titems_empty):
            Grabber(items=[])

    def test_err_no_items_found_do_raise_false(self):
        with pytest.raises(GrabberError, match=Grabber._tnone_found):
            Grabber(items={}, do_raise=False)

    def test_err_no_items_found_do_raise_true(self):
        with pytest.raises(GrabberError, match=Grabber._terrors_mid):
            Grabber(items={}, do_raise=True)

    def test_from_json(self):
        grabber = Grabber.from_json(items=fake_json())
        assert grabber.count_found == grabber.count_supplied == CNT

    def test_dicts(self):
        grabber = Grabber(items=fake_ids())
        assert grabber.count_found == grabber.count_supplied == CNT

    def test_bad_item_type(self):
        grabber = Grabber(items=fake_ids(other=[[]]))
        assert grabber.count_found == CNT
        assert grabber.count_supplied == CNT + 1
        assert Hunter._tbadtype in grabber.hunters[-1].error

    def test_bad_item_axid(self):
        grabber = Grabber(items=fake_ids(other=fake_ids(cnt=1, length=33)))
        assert grabber.count_found == CNT
        assert grabber.count_supplied == CNT + 1
        assert Hunter._tdict_n_keys in grabber.hunters[-1].error

    def test_from_json_reorder(self):
        grabber = Grabber.from_json(items=fake_json(col=AXID.column_title))
        assert str(grabber)
        assert repr(grabber)
        for hunter in grabber.hunters:
            assert str(hunter)
            assert repr(hunter)
        assert grabber.keys[0] == AXID.column_title
        assert grabber.count_found == grabber.count_supplied == CNT

    def test_from_json_path(self, tmp_path):
        filename = "test.json"
        path = tmp_path / filename
        path.write_text(fake_json())
        grabber = Grabber.from_json_path(path=path)
        assert grabber.count_found == grabber.count_supplied == CNT

    def test_from_jsonl(self):
        grabber = Grabber.from_jsonl(items=fake_jsonl())
        assert grabber.count_found == grabber.count_supplied == CNT

    def test_from_jsonl_path(self, tmp_path):
        filename = "test.jsonl"
        path = tmp_path / filename
        path.write_text(fake_jsonl())
        grabber = Grabber.from_jsonl_path(path=path)
        assert grabber.count_found == grabber.count_supplied == CNT

    def test_from_csv(self):
        grabber = Grabber.from_csv(items=fake_csv())
        assert grabber.count_found == grabber.count_supplied == CNT

    def test_from_csv_path(self, tmp_path):
        filename = "test.csv"
        path = tmp_path / filename
        path.write_text(fake_csv())
        grabber = Grabber.from_csv_path(path=path)
        assert grabber.count_found == grabber.count_supplied == CNT

    def test_from_text(self):
        grabber = Grabber.from_text(items="#\n\n" + fake_csv())
        assert grabber.count_found == CNT
        assert grabber.count_supplied == CNT + 3

    def test_from_text_path(self, tmp_path):
        filename = "test.txt"
        path = tmp_path / filename
        path.write_text(fake_csv())
        grabber = Grabber.from_text_path(path=path)
        assert grabber.count_found == CNT
        assert grabber.count_supplied == CNT + 1
