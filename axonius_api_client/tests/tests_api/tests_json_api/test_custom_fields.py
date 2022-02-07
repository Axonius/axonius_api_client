import datetime

import marshmallow
import pytest

from axonius_api_client.api import json_api


class TestSupporting:
    def test_load_date(self):
        ret = json_api.custom_fields.load_date(value="2020-01-01")
        assert isinstance(ret, datetime.datetime)
        ret2 = json_api.custom_fields.load_date(value=ret)
        assert ret == ret2

    def test_dump_date(self):
        date = datetime.datetime.now()
        ret = json_api.custom_fields.dump_date(value=date)
        assert isinstance(ret, str) and ret


class TestSchemaBool:
    def test_deserialize_none(self):
        field = json_api.custom_fields.SchemaBool(allow_none=True)
        ret = field._deserialize(value=None, attr="test", data={"test": None})
        assert ret is None

    def test_deserialize_none_fail(self):
        field = json_api.custom_fields.SchemaBool()
        with pytest.raises(marshmallow.ValidationError):
            field._deserialize(value=None, attr="test", data={"test": None})

    def test_deserialize_fail(self):
        field = json_api.custom_fields.SchemaBool()
        with pytest.raises(marshmallow.ValidationError):
            field._deserialize(value="MOO", attr="test", data={"test": None})

    def test_deserialize_success(self):
        field = json_api.custom_fields.SchemaBool()
        ret = field._deserialize(value="y", attr="test", data={"test": None})
        assert ret is True

    def test_serialize_none(self):
        field = json_api.custom_fields.SchemaBool(allow_none=True)
        ret = field._serialize(value=None, attr="test", obj=None)
        assert ret is None

    def test_serialize_none_fail(self):
        field = json_api.custom_fields.SchemaBool()
        with pytest.raises(marshmallow.ValidationError):
            field._serialize(value=None, attr="test", obj=None)

    def test_serialize_fail(self):
        field = json_api.custom_fields.SchemaBool()
        with pytest.raises(marshmallow.ValidationError):
            field._serialize(value="MOO", attr="test", obj=None)

    def test_serialize_success(self):
        field = json_api.custom_fields.SchemaBool()
        ret = field._serialize(value="y", attr="test", obj=None)
        assert ret is True


class TestSchemaDate:
    def test_deserialize_none(self):
        field = json_api.custom_fields.SchemaDatetime(allow_none=True)
        ret = field._deserialize(value=None, attr="test", data={"test": None})
        assert ret is None

    def test_deserialize_none_fail(self):
        field = json_api.custom_fields.SchemaDatetime()
        with pytest.raises(marshmallow.ValidationError):
            field._deserialize(value=None, attr="test", data={"test": None})

    def test_deserialize_fail(self):
        field = json_api.custom_fields.SchemaDatetime()
        with pytest.raises(marshmallow.ValidationError):
            field._deserialize(value="MOO", attr="test", data={"test": None})

    def test_deserialize_success(self):
        field = json_api.custom_fields.SchemaDatetime()
        ret = field._deserialize(value="2020-01-01", attr="test", data={"test": None})
        assert isinstance(ret, datetime.datetime)

    def test_serialize_none(self):
        field = json_api.custom_fields.SchemaDatetime(allow_none=True)
        ret = field._serialize(value=None, attr="test", obj=None)
        assert ret is None

    def test_serialize_success(self):
        field = json_api.custom_fields.SchemaDatetime()
        ret = field._serialize(value=datetime.datetime.now(), attr="test", obj=None)
        assert isinstance(ret, str)
