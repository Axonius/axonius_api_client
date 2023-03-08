# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client."""
# import pytest

import dataclasses

from axonius_api_client.data import BaseData, BaseEnum, PropsData


class TestBaseData:
    def test_str_repr_init(self):
        @dataclasses.dataclass
        class BadWolf(BaseData):
            name: str

        obj = BadWolf(name="x")
        assert isinstance(obj, BaseData)
        assert isinstance(obj, BadWolf)
        assert "BadWolf(name='x')" in str(obj)
        assert "BadWolf(name='x')" in repr(obj)
        assert obj.to_dict() == {"name": "x"}

    def test_to_dict(self):
        @dataclasses.dataclass
        class BadWolf(BaseData):
            name: str
            foo: str = "boo"

        obj = BadWolf(name="x")
        obj_dict = obj.to_dict()
        obj_dict_exp = {"name": "x", "foo": "boo"}
        assert obj_dict == obj_dict_exp

    def test_get_fields(self):
        @dataclasses.dataclass
        class BadWolf(BaseData):
            name: str
            foo: str = "boo"

        cls_names = [x.name for x in BadWolf.get_fields()]
        cls_names_exp = ["name", "foo"]
        assert cls_names == cls_names_exp

        cls_defaults = [
            x.default
            for x in BadWolf.get_fields()
            if not isinstance(x.default, dataclasses._MISSING_TYPE)
        ]
        cls_defaults_exp = ["boo"]
        assert cls_defaults == cls_defaults_exp

        obj = BadWolf(name="x")

        obj_names = [x.name for x in obj.get_fields()]
        assert obj_names == cls_names_exp

        obj_defaults = [
            x.default
            for x in BadWolf.get_fields()
            if not isinstance(x.default, dataclasses._MISSING_TYPE)
        ]
        assert obj_defaults == cls_defaults_exp


class TestPropsData:
    def test_str_repr_init(self):
        @dataclasses.dataclass
        class BadWolf(PropsData):
            raw: dict

            @property
            def _properties(self):
                return ["name"]

            @property
            def name(self):
                return self.raw["name"]

        obj = BadWolf(raw={"name": "x"})
        assert str(obj)
        assert repr(obj)
        assert obj.to_dict() == {"name": "x"}


class TestBaseEnum:
    def test_iter(self):
        class BadWolf(BaseEnum):
            name = "badwolf"

        assert [x.name for x in BadWolf] == ["name"]
        assert [x.value for x in BadWolf] == ["badwolf"]
        assert str(BadWolf.name) == "badwolf"
