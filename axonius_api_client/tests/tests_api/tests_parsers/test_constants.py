# -*- coding: utf-8 -*-
"""Test suite."""
import pytest

from axonius_api_client.constants.fields import Operators, OperatorTypeMaps
from axonius_api_client.exceptions import NotFoundError, UnknownFieldSchema


class TestOperatorTypeMaps:
    def test_get_type_map(self):
        field = {"type": "string", "name_qual": "badwolf"}
        type_map = OperatorTypeMaps.get_type_map(field=field)
        assert type_map == OperatorTypeMaps.string

    def test_get_type_map_invalid(self):
        field = {"type": "badwolf", "name_qual": "badwolf"}
        with pytest.warns(UnknownFieldSchema):
            OperatorTypeMaps.get_type_map(field=field)

    def test_get_operator(self):
        field = {
            "type": "string",
            "name_qual": "badwolf",
            "name": "badwolf",
            "parent": "moo",
        }

        op = OperatorTypeMaps.get_operator(field=field, operator="equals")
        assert op == Operators.equals_str

    def test_get_operator_invalid(self):
        field = {
            "type": "string",
            "name_qual": "badwolf",
            "name": "badwolf",
            "parent": "moo",
        }
        with pytest.raises(NotFoundError) as exc:
            OperatorTypeMaps.get_operator(field=field, operator="equax")

        assert "sub field of" in str(exc.value)

    def test_get_operator_invalid_root(self):
        field = {
            "type": "string",
            "name_qual": "badwolf",
            "name": "badwolf",
            "parent": "root",
        }
        with pytest.raises(NotFoundError) as exc:
            OperatorTypeMaps.get_operator(field=field, operator="equax")
        assert "sub field of" not in str(exc.value)
