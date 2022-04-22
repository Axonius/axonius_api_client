import dataclasses
from typing import List, Type

import pytest
import requests
from axonius_api_client.api import json_api
from axonius_api_client.api.api_endpoints import ApiEndpoint, ApiEndpointGroup, ApiEndpoints
from axonius_api_client.exceptions import (
    InvalidCredentials,
    JsonInvalidError,
    RequestFormatObjectError,
    RequestFormatPathError,
    RequestLoadObjectError,
    RequestMissingArgsError,
    RequestObjectTypeError,
    ResponseLoadObjectError,
    ResponseNotOk,
)
from axonius_api_client.http import Http
from axonius_api_client.tools import get_subcls

from ..utils import get_auth, get_url

MODELS_EXCLUDE = [
    json_api.base.BaseModel,
    json_api.resources.PaginationRequest,
    json_api.resources.PageSortRequest,
    json_api.assets.AssetTypeHistoryDates,
    json_api.adapters.Cnx,
    json_api.system_settings.SystemSettingsUpdate,
    json_api.assets.AssetTypeHistoryDate,
    json_api.adapters.AdapterNodeCnx,
    json_api.adapters.AdapterClientsCount,
    json_api.adapters.AdapterNode,
    json_api.saved_queries.Folder,
    json_api.data_scopes.DataScope,
]

SCHEMAS_EXCLUDE = [
    json_api.base.BaseSchema,
    json_api.base.BaseSchemaJson,
    json_api.central_core.AdditionalDataAws,
    json_api.system_settings.SystemSettingsUpdateSchema,
]


def get_model_classes() -> List[Type[json_api.base.BaseModel]]:
    return [
        x
        for x in get_subcls(json_api.base.BaseModel)
        if x not in MODELS_EXCLUDE and "tests." not in str(x)
    ]


def get_schema_classes() -> List[Type[json_api.base.BaseSchema]]:
    return [
        x
        for x in get_subcls(json_api.base.BaseSchema)
        if x not in SCHEMAS_EXCLUDE and "tests." not in str(x)
    ]


GROUPS_SUBCLS: List[Type[ApiEndpointGroup]] = get_subcls(ApiEndpointGroup)
GROUPS_SUBCLS_USED: List[Type[ApiEndpointGroup]] = [
    x.__class__ for x in ApiEndpoints.get_groups().values()
]


class TestApiEndpoint:
    def test_response_as_text(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
            response_as_text=True,
        )

        ax_url = get_url(request)
        http = Http(url=ax_url)
        response = endpoint.perform_request_raw(http=http)
        ret = endpoint.handle_response(http=None, response=response)
        assert ret == response.text

    def test_wrong_model_cls(self):
        with pytest.raises(ValueError):
            ApiEndpoint(
                method="get",
                path="",
                request_schema_cls=None,
                request_model_cls=pytest,
                response_schema_cls=None,
                response_model_cls=None,
            )

    def test_wrong_schema_cls(self):
        with pytest.raises(ValueError):
            ApiEndpoint(
                method="get",
                path="",
                request_schema_cls=pytest,
                request_model_cls=None,
                response_schema_cls=None,
                response_model_cls=None,
            )

    def test_dump_path_from_obj(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="test/{value}",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        request_obj = json_api.generic.BoolValue(value=False)
        exp = "test/False"
        ret = endpoint.dump_path(request_obj=request_obj)
        assert ret == exp

    def test_dump_path_from_kwargs(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="test/{value}/{arg1}",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        request_obj = json_api.generic.BoolValue(value=False)
        exp = "test/False/moo"
        ret = endpoint.dump_path(request_obj=request_obj, arg1="moo")
        assert ret == exp

    def test_dump_path_empty(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="test/value/arg1",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        request_obj = json_api.generic.BoolValue(value=False)
        exp = "test/value/arg1"
        ret = endpoint.dump_path(request_obj=request_obj, arg1="moo")
        assert ret == exp

    def test_dump_path_no_obj(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="test/value/{arg1}",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        exp = "test/value/moo"
        ret = endpoint.dump_path(arg1="moo")
        assert ret == exp

    def test_dump_path_err(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="test/value/{arg1}",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        with pytest.raises(RequestFormatPathError):
            endpoint.dump_path()

    def test_check_request_obj(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        request_obj = json_api.generic.BoolValue(value=False)
        endpoint.check_request_obj(request_obj=request_obj)

    def test_check_request_obj_fail(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        request_obj = json_api.generic.IntValue(value=2)
        with pytest.raises(RequestObjectTypeError):
            endpoint.check_request_obj(request_obj=request_obj)

    def test_check_missing_args(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
            http_args_required=[],
        )
        endpoint.check_missing_args(args={})

    def test_check_missing_args_success(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
            http_args_required=["wah"],
        )
        endpoint.check_missing_args(args={"wah": 2})

    def test_check_missing_args_fail(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
            http_args_required=["wah"],
        )
        with pytest.raises(RequestMissingArgsError):
            endpoint.check_missing_args(args={})

    def test_get_response_json_fail(self, request):
        endpoint = ApiEndpoint(
            method="get",
            path="",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
        )

        ax_url = get_url(request)
        http = Http(url=ax_url)
        response = endpoint.perform_request_raw(http=http)
        with pytest.raises(JsonInvalidError):
            endpoint.get_response_json(response=response)

    def test_dump_object_request_as_none(self, request, monkeypatch):
        endpoint = ApiEndpoint(
            method="get",
            path="",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
            request_as_none=True,
        )
        request_obj = json_api.generic.BoolValue(value=False)
        exp = {}
        ret = endpoint.dump_object(request_obj=request_obj)
        assert isinstance(ret, dict)
        assert ret == exp

    def test_dump_object_post(self, request, monkeypatch):
        endpoint = ApiEndpoint(
            method="post",
            path="",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        request_obj = json_api.generic.BoolValue(value=False)
        exp = {"json": {"data": {"type": "bool_value_schema", "attributes": {"value": False}}}}
        ret = endpoint.dump_object(request_obj=request_obj)
        assert isinstance(ret, dict)
        assert ret == exp

    def test_dump_object_get(self, request, monkeypatch):
        endpoint = ApiEndpoint(
            method="get",
            path="",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        request_obj = json_api.generic.BoolValue(value=False)
        exp = {"params": {"value": False}}
        ret = endpoint.dump_object(request_obj=request_obj)
        assert isinstance(ret, dict)
        assert ret == exp

    def test_dump_object_fail_not_model(self, request, monkeypatch):
        endpoint = ApiEndpoint(
            method="get",
            path="",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        request_obj = {"i am not a": "model"}
        with pytest.raises(RequestFormatObjectError):
            endpoint.dump_object(request_obj=request_obj)

    def test_dump_object_fail_serialization(self, request, monkeypatch):
        endpoint = ApiEndpoint(
            method="post",
            path="",
            request_schema_cls=json_api.generic.BoolValueSchema,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        request_obj = json_api.generic.BoolValue(value="MANANANANANA")
        with pytest.raises(RequestFormatObjectError):
            endpoint.dump_object(request_obj=request_obj)

    def test_get_response_json(self, request):
        endpoint = ApiEndpoints.system_settings.feature_flags_get
        auth = get_auth(request)

        response = endpoint.perform_request_raw(http=auth.http)
        ret = endpoint.get_response_json(response=response)
        assert isinstance(ret, dict)
        assert "data" in ret

    def test_check_response_json(self, request):
        endpoint = ApiEndpoints.system_settings.feature_flags_get
        auth = get_auth(request)

        response = endpoint.perform_request_raw(http=auth.http)
        endpoint.check_response_status(http=auth.http, response=response)

    def test_check_response_json_401(self, request, monkeypatch):
        endpoint = ApiEndpoints.system_settings.feature_flags_get
        auth = get_auth(request)

        response = endpoint.perform_request_raw(http=auth.http)
        monkeypatch.setattr(response, "status_code", 401)
        with pytest.raises(InvalidCredentials):
            endpoint.check_response_status(http=auth.http, response=response)

    def test_check_response_json_bad(self, request, monkeypatch):
        endpoint = ApiEndpoints.system_settings.feature_flags_get
        auth = get_auth(request)

        response = endpoint.perform_request_raw(http=auth.http)
        monkeypatch.setattr(response, "status_code", 500)
        with pytest.raises(ResponseNotOk):
            endpoint.check_response_status(http=auth.http, response=response)

    def test_check_response_json_hook_status_skip(self, request, monkeypatch):
        def hook(http, response, **kwargs):
            assert isinstance(http, Http)
            assert isinstance(response, requests.Response)
            return True

        endpoint = ApiEndpoints.system_settings.feature_flags_get
        auth = get_auth(request)

        response = endpoint.perform_request_raw(http=auth.http)
        monkeypatch.setattr(response, "status_code", 500)

        endpoint.check_response_status(http=auth.http, response=response, response_status_hook=hook)

    def test_check_response_json_hook(self, request, monkeypatch):
        def hook(http, response, **kwargs):
            assert isinstance(http, Http)
            assert isinstance(response, requests.Response)

        endpoint = ApiEndpoints.system_settings.feature_flags_get
        auth = get_auth(request)

        response = endpoint.perform_request_raw(http=auth.http)
        endpoint.check_response_status(http=auth.http, response=response, response_status_hook=hook)

    def test_check_response_json_hook_fail(self, request, monkeypatch):
        class Failure(Exception):
            pass

        def hook(http, response, **kwargs):
            assert isinstance(http, Http)
            assert isinstance(response, requests.Response)
            assert kwargs["other"] == 2
            raise Failure

        endpoint = ApiEndpoints.system_settings.feature_flags_get
        auth = get_auth(request)

        response = endpoint.perform_request_raw(http=auth.http)
        with pytest.raises(Failure):
            endpoint.check_response_status(
                http=auth.http, response=response, response_status_hook=hook, other=2
            )

    def test_load_response_unloaded(self, request):
        endpoint = ApiEndpoints.system_settings.feature_flags_get
        auth = get_auth(request)
        response = endpoint.perform_request_raw(http=auth.http)
        data = response.json()
        ret = endpoint.load_response(data=data, http=auth.http, unloaded=True)
        assert ret == data

    def test_load_response(self, request):
        endpoint = ApiEndpoints.system_settings.feature_flags_get
        auth = get_auth(request)
        response = endpoint.perform_request_raw(http=auth.http)
        data = response.json()
        ret = endpoint.load_response(data=data, http=auth.http)
        assert isinstance(ret, endpoint.response_model_cls)

    def test_load_response_fail(self, request):
        endpoint = ApiEndpoints.system_settings.feature_flags_get
        data = {"wah": 2}
        with pytest.raises(ResponseLoadObjectError):
            endpoint.load_response(data=data, http=None)

    def test_attr_request_load_cls(self):
        endpoint = ApiEndpoint(
            method="get",
            path="badwolf",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
        )
        assert endpoint.request_load_cls is None
        endpoint = ApiEndpoint(
            method="get",
            path="badwolf",
            request_schema_cls=None,
            request_model_cls=json_api.generic.BoolValue,
            response_schema_cls=None,
            response_model_cls=None,
        )
        assert endpoint.request_load_cls == json_api.generic.BoolValue

    def test_attr_response_load_cls(self):
        endpoint = ApiEndpoint(
            method="get",
            path="badwolf",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
        )
        assert endpoint.response_load_cls is None
        endpoint = ApiEndpoint(
            method="get",
            path="badwolf",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=json_api.generic.BoolValue,
        )
        assert endpoint.response_load_cls == json_api.generic.BoolValue

        endpoint = ApiEndpoint(
            method="get",
            path="badwolf",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=json_api.generic.BoolValueSchema,
            response_model_cls=json_api.generic.BoolValue,
        )
        assert endpoint.response_load_cls == json_api.generic.BoolValueSchema

    def test_json_invalid(self, request):
        ax_url = get_url(request)

        http = Http(url=ax_url, certwarn=False)
        endpoint = ApiEndpoint(
            method="get",
            path="badwolf",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
        )
        with pytest.raises(JsonInvalidError):
            endpoint.perform_request(http=http)

    def test_load_request_load_err(self):
        with pytest.raises(RequestLoadObjectError):
            ApiEndpoints.system_users.create.load_request(test=1)

    def test_load_request_no_cls(self):
        endpoint = ApiEndpoint(
            method="get",
            path="badwolf",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
        )
        exp = {"test": 1}
        ret = endpoint.load_request(test=1)
        assert ret == exp

    def test_load_request_no_cls_no_args(self):
        endpoint = ApiEndpoint(
            method="get",
            path="badwolf",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
        )
        exp = None
        ret = endpoint.load_request()
        assert ret == exp

    def test_load_request(self):
        @dataclasses.dataclass
        class SomeDataModel(json_api.base.BaseModel):
            test: int

        endpoint = ApiEndpoint(
            method="get",
            path="badwolf",
            request_schema_cls=None,
            request_model_cls=SomeDataModel,
            response_schema_cls=None,
            response_model_cls=None,
        )
        exp = SomeDataModel(test=1)
        ret = endpoint.load_request(test=1)
        assert ret == exp


class TestApiEndpointGroups:
    def test_strs(self):
        for group_name, group in ApiEndpoints.get_groups().items():
            assert group_name in str(ApiEndpoints)
            for endpoint_name, endpoint in group.get_endpoints().items():
                assert endpoint_name in str(group)

    def test_groups_used(self):
        for group in GROUPS_SUBCLS:
            err = f"{group} not in use in {GROUPS_SUBCLS_USED}"
            assert group in GROUPS_SUBCLS_USED, err

    def test_schemas_models_match(self):
        for group in GROUPS_SUBCLS:
            for name, endpoint in group.get_endpoints().items():
                if endpoint.request_schema_cls:
                    if endpoint.request_model_cls:
                        model_from_schema = endpoint.request_schema_cls.get_model_cls()
                        assert model_from_schema == endpoint.request_model_cls

                if endpoint.request_model_cls:
                    if endpoint.request_schema_cls:
                        schema_from_model = endpoint.request_model_cls.get_schema_cls()
                        assert schema_from_model == endpoint.request_schema_cls

                if endpoint.response_schema_cls:
                    if endpoint.response_model_cls:
                        model_from_schema = endpoint.response_schema_cls.get_model_cls()
                        assert model_from_schema == endpoint.response_model_cls

                if endpoint.response_model_cls:
                    if endpoint.response_schema_cls:
                        schema_from_model = endpoint.response_model_cls.get_schema_cls()
                        assert schema_from_model == endpoint.response_schema_cls

    def test_models_used(self):
        cls_used = []

        for group in GROUPS_SUBCLS:
            for name, endpoint in group.get_endpoints().items():
                cls_used += [endpoint.request_model_cls, endpoint.response_model_cls]

        for cls in get_model_classes():
            err = f"{cls} not in use by any api endpoint"
            assert cls in cls_used, err

    def test_schemas_used(self):
        cls_used = []

        for group in GROUPS_SUBCLS:
            for name, endpoint in group.get_endpoints().items():
                cls_used += [endpoint.request_schema_cls, endpoint.response_schema_cls]

        for cls in get_schema_classes():
            err = f"{cls} not in use by any api endpoint"
            assert cls in cls_used, err
