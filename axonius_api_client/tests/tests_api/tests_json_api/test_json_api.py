import dataclasses

import marshmallow
import pytest

from axonius_api_client.api import json_api
from axonius_api_client.api.json_api.base import BaseModel, BaseSchema, BaseSchemaJson
from axonius_api_client.exceptions import ExtraAttributeWarning, SchemaError

from ..test_api_endpoints import get_model_classes, get_schema_classes


class TestJsonApi:
    def test_model_schema_links(self):
        for model in get_model_classes():
            schema_from_model = model.get_schema_cls()
            if schema_from_model is not None:
                model_from_schema = schema_from_model.get_model_cls()
                err = f"model {model} != {model_from_schema} from schema {schema_from_model}"
                assert model_from_schema == model, err

    def test_schema_model_links(self):
        for schema in get_schema_classes():
            if schema == BaseSchemaJson:
                continue

            model_from_schema = schema.get_model_cls()
            if model_from_schema != dict:
                schema_from_model = model_from_schema.get_schema_cls()
                err = f"schema {schema} != {schema_from_model} from model {model_from_schema}"
                assert schema_from_model == schema, err

    def test_json_api_load_response(self):
        @dataclasses.dataclass
        class SomeModel(BaseModel):
            test: int

            @staticmethod
            def get_schema_cls():
                return SomeSchema

        class SomeSchema(BaseSchemaJson):
            test = marshmallow.fields.Int()

            class Meta:
                """Pass."""

                type_ = "some_schema"

            @staticmethod
            def get_model_cls():
                return SomeModel

        with pytest.raises(SchemaError) as exc:
            SomeModel.load_response(data=1)
        assert "Data to load must be a dictionary" in str(exc.value)

        with pytest.raises(SchemaError) as exc:
            SomeSchema.load_response(data="x")
        assert "Data to load must be a dictionary" in str(exc.value)

        with pytest.raises(SchemaError) as exc:
            SomeModel.load_response(data={})
        assert "Object must include `data` key." in str(exc.value)

        with pytest.raises(SchemaError) as exc:
            SomeSchema.load_response(data={})
        assert "Object must include `data` key." in str(exc.value)

        with pytest.raises(SchemaError) as exc:
            SomeSchema.load_response(
                data={"data": {"type": "wrong_type", "attributes": {"duh": "duh"}}}
            )
        assert 'Invalid type. Expected "some_schema"' in str(exc.value)

        exp = SomeModel(test=1)
        ret = SomeSchema.load_response(
            data={"data": {"type": "some_schema", "attributes": {"test": 1}}}
        )
        assert ret == exp
        # with warnings.catch_warnings():
        #     if json_api.base.EXTRA_WARN:
        #         warnings.simplefilter("ignore", ApiWarning)

        with pytest.warns(ExtraAttributeWarning):
            ret = SomeSchema.load_response(
                data={"data": {"type": "some_schema", "attributes": {"test": 1, "extra": 2}}}
            )
        assert ret.test == 1
        assert ret.extra_attributes == {"extra": 2}

    def test_non_json_api_load_response(self):
        @dataclasses.dataclass
        class SomeModel(BaseModel):
            test: int

            @staticmethod
            def get_schema_cls():
                return SomeSchema

        class SomeSchema(BaseSchema):
            test = marshmallow.fields.Int()

            @staticmethod
            def get_model_cls():
                return SomeModel

        with pytest.raises(SchemaError) as exc:
            SomeModel.load_response(data=1)
        assert "Data to load must be a dictionary or list" in str(exc.value)

        with pytest.raises(SchemaError) as exc:
            SomeSchema.load_response(data=1)
        assert "Data to load must be a dictionary or list" in str(exc.value)

        # with warnings.catch_warnings():
        #     if json_api.base.EXTRA_WARN:
        #         warnings.simplefilter("ignore", ApiWarning)

        with pytest.warns(ExtraAttributeWarning):
            ret = SomeSchema.load_response(data={"test": 1, "extra": 2})

        assert ret.test == 1
        assert ret.extra_attributes == {"extra": 2}

        exp = SomeModel(test=1)
        ret = SomeSchema.load_response(data={"test": 1})
        assert ret == exp

    def test_dict_load_response(self):
        class SomeSchema(BaseSchema):
            test = marshmallow.fields.Int()

            @staticmethod
            def get_model_cls():
                return dict

        with pytest.raises(SchemaError) as exc:
            SomeSchema.load_response(data=1)
        assert "Data to load must be a dictionary or list" in str(exc.value)

        exp = {"test": 1, "extra": 2}

        # with warnings.catch_warnings():
        #     if json_api.base.EXTRA_WARN:
        #         warnings.simplefilter("ignore", ApiWarning)

        ret = SomeSchema.load_response(data={"test": 1, "extra": 2})
        assert ret == exp

        exp = {"test": 1}
        ret = SomeSchema.load_response(data={"test": 1})
        assert ret == exp

    def test_model_no_schema_load_response(self):
        @dataclasses.dataclass
        class SomeModel(BaseModel):
            test: int

            @staticmethod
            def get_schema_cls():
                return None

        with pytest.raises(SchemaError) as exc:
            SomeModel.load_response(data=1)
        assert "Data to load must be a dictionary or list" in str(exc.value)

        exp = SomeModel(test=1)
        ret = SomeModel.load_response(data={"test": 1})
        assert ret == exp
        assert ret["test"] == 1
        ret["test"] = 2
        assert ret.test == 2

    def test_dump_request_dataclasses_json_schema(self):
        @dataclasses.dataclass
        class SomeModel(BaseModel):
            test: int

            @staticmethod
            def get_schema_cls():
                return None

        exp = {"test": 1}
        data = SomeModel(test=1)
        ret = data.dump_request()
        assert ret == exp

        ret = data.dump_request(schema_cls=data.schema)
        assert ret == exp

    def test_dump_request_marshmallow_json_schema(self):
        @dataclasses.dataclass
        class SomeModel(BaseModel):
            test: int

            @staticmethod
            def get_schema_cls():
                return SomeSchema

        class SomeSchema(BaseSchemaJson):
            test = marshmallow.fields.Int()

            class Meta:
                """Pass."""

                type_ = "some_schema"

            @staticmethod
            def get_model_cls():
                return SomeModel

        exp = {"data": {"attributes": {"test": 1}, "type": "some_schema"}}
        data = SomeModel(test=1)
        ret = data.dump_request()
        assert ret == exp

        ret = data.dump_request(schema_cls=SomeSchema)
        assert ret == exp

        exp = {"test": 1}
        ret = data.dump_request(schema_cls=data.schema)
        assert ret == exp

    def test_dump_request_params(self):
        data = json_api.resources.ResourcesGet(page={"limit": 20, "offset": 3})
        exp = {"page[limit]": 20, "page[offset]": 3, "get_metadata": True}
        ret = data.dump_request_params()
        assert ret == exp
