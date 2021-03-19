# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import logging
from typing import Any, List, Optional, Type, Union

import dataclasses_json
import marshmallow
import marshmallow_jsonapi
import requests

from ..connect import Connect
from ..constants.logs import LOG_LEVEL_API
from ..exceptions import (ApiError, InvalidCredentials, JsonApiError,
                          JsonInvalid, ResponseNotOk, UnsupportedVersion,
                          ValidationError)
from ..logs import get_obj_log
from ..tools import combo_dicts, json_reload, listify

ComplexTypes = Union[dict, list, tuple]
DataTypes = Union["DataModel", Any]


class ApiModel:
    """API model base class."""

    def __init__(self, client: Connect, **kwargs):
        """Mixins for API Models.

        Args:
            client: Connection client
            **kwargs: passed to :meth:`_init`
        """
        log_level = kwargs.get("log_level", LOG_LEVEL_API)
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        """Logger for this object."""

        self.CLIENT = client
        """:obj:`axonius_api_client.connect.Connect` Connection client."""

        self.HTTP = client.HTTP

        self._init(**kwargs)

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        pass

    def __str__(self) -> str:
        """Show info for this model object."""
        cls = self.__class__
        return f"{cls.__module__}.{cls.__name__} - {self.CLIENT!r}"

    def __repr__(self) -> str:
        """Show info for this model object."""
        return self.__str__()


@dataclasses.dataclass
class ApiEndpoint:
    """Pass."""

    method: str
    path: str

    request_schema_cls: Optional[type]
    request_model_cls: Optional[type]
    response_schema_cls: Optional[type]
    response_model_cls: Optional[type]

    http_args: dict = dataclasses.field(default_factory=dict)
    http_args_required: List[str] = dataclasses.field(default_factory=list)

    request_as_none: bool = False
    response_as_text: bool = False
    log_level: str = "debug"

    def __str__(self):
        """Pass."""
        lines = [
            f"ApiEndpoint Method={self.method!r}, path={self.path!r}",
            f"Request Schema={self.request_schema_cls}",
            f"Request Model={self.request_model_cls}",
            f"Response Schema={self.response_schema_cls}",
            f"Response Model={self.response_model_cls}",
        ]
        return "\n  ".join(lines)

    @property
    def log(self) -> logging.Logger:
        """Pass."""
        return get_obj_log(obj=self, level=self.log_level)

    def perform_request(
        self,
        client: Connect,
        request_obj: Optional[DataTypes] = None,
        **kwargs,
    ) -> DataTypes:
        """Pass."""
        kwargs["response"] = self.perform_request_raw(
            client=client, request_obj=request_obj, **kwargs
        )
        return self.handle_response(client=client, **kwargs)

    def perform_request_raw(
        self,
        client: Connect,
        request_obj: Optional[DataTypes] = None,
        **kwargs,
    ) -> requests.Response:
        """Pass."""
        http_args = self.get_http_args(request_obj=request_obj, **kwargs)
        response = client.HTTP(**http_args)
        return response

    def load_request(self, **kwargs) -> Optional[DataTypes]:
        """Pass."""
        if self.request_model_cls:
            this_kwargs = {"api_endpoint": self}
            this_kwargs = combo_dicts(kwargs, this_kwargs)
            return self.request_model_cls._load_request(**this_kwargs)
        return kwargs or None

    def load_response(self, data: Any, client: Connect, **kwargs) -> DataTypes:
        """Pass."""
        if kwargs.get("unloaded"):
            return data

        if self.response_schema_cls:
            use = self.response_schema_cls
        elif self.response_model_cls:
            use = self.response_model_cls
        else:
            use = None

        if use:
            this_kwargs = {"api_endpoint": self}
            this_kwargs = combo_dicts(kwargs, this_kwargs)
            data = use._load_response(data=data, client=client, **this_kwargs)

        return data

    def handle_response(self, client: Connect, response: requests.Response, **kwargs) -> DataTypes:
        """Pass."""
        if self.response_as_text:
            self.handle_response_status(client=client, response=response, **kwargs)
            return response.text

        data = self.handle_response_json(client=client, response=response, **kwargs)

        this_kwargs = {"data": data}
        this_kwargs = combo_dicts(kwargs, this_kwargs)

        self.handle_response_status(client=client, response=response, **this_kwargs)

        return self.load_response(client=client, response=response, **this_kwargs)

    def handle_response_json(self, client: Connect, response: requests.Response, **kwargs) -> dict:
        """Get the JSON from a response.

        Args:
            response: :obj:`requests.Response` object to check

        Raises:
            :exc:`JsonInvalid`: if response has invalid json
        """
        try:
            data = response.json()
        except Exception as exc:
            raise JsonInvalid(msg="Response has invalid JSON", response=response, exc=exc)
        return data

    def handle_response_status(self, client: Connect, response: requests.Response, **kwargs):
        """Check the status code of a response.

        Args:
            response: :obj:`requests.Response` object to check

        Raises:
            :exc:`.InvalidCredentials`: if response has has a 401 status code
            :exc:`.ResponseNotOk`: if response has a bad status code
        """
        hook = kwargs.get("response_status_hook")

        if callable(hook):
            hook(client=client, response=response, **kwargs)

        if response.status_code == 401:
            raise InvalidCredentials(msg="Invalid credentials", response=response)

        try:
            response.raise_for_status()
        except Exception as exc:
            raise ResponseNotOk(
                msg=f"Response has a bad HTTP status code {response.status_code}",
                response=response,
                exc=exc,
            )

    def get_http_args(
        self,
        request_obj: Optional[DataTypes] = None,
        http_args: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        """Pass."""
        args = {}
        args["method"] = self.method

        if request_obj is not None:
            self.check_request_obj(request_obj=request_obj)

            this_kwargs = {"path": self.path}
            this_kwargs = combo_dicts(kwargs, this_kwargs)
            args["path"] = request_obj._dump_request_path(**this_kwargs)

            if not self.request_as_none:
                this_kwargs = {"api_endpoint": self, "schema_cls": self.request_schema_cls}
                this_kwargs = combo_dicts(kwargs, this_kwargs)

                if self.method == "get":
                    args["params"] = request_obj._dump_request_params(**this_kwargs)
                else:
                    args["json"] = request_obj._dump_request(**this_kwargs)

        else:
            args["path"] = self.path.format(**kwargs)

        args.update(self.http_args or {})
        args.update(http_args or {})

        for arg in self.http_args_required:
            if not args.get(arg):
                msgs = [
                    f"Missing required HTTP argument {arg!r}",
                    f"While in {self}",
                    f"HTTP arguments:\n{json_reload(args)}",
                    f"Missing required HTTP argument {arg!r}",
                ]
                raise ApiError("\n\n".join(msgs))
        return args

    def check_request_obj(self, request_obj: DataTypes):
        """Pass."""
        model_check = self.request_model_cls
        if model_check and not isinstance(request_obj, model_check):
            otype = type(request_obj)
            msg = f"Request object must be of type {model_check!r}, not of type {otype!r}"
            raise ApiError(msg)


class DataCommon:
    """Pass."""

    @classmethod
    def _check_version(cls, data: Any, api_endpoint: ApiEndpoint = None):
        """Pass."""
        if not isinstance(data, dict) or (isinstance(data, dict) and "data" not in data):
            raise UnsupportedVersion(schema=cls, data=data, api_endpoint=api_endpoint)

    @classmethod
    def _post_load_attrs(cls, loaded: DataTypes, client: Connect = None, **kwargs):
        """Pass."""
        for item in listify(loaded):
            if isinstance(item, DataModel):
                item.CLIENT = client

    @classmethod
    def _load_schema(
        cls,
        schema: marshmallow.Schema,
        data: dict,
        client: Connect,
        api_endpoint: ApiEndpoint,
        **kwargs,
    ) -> DataTypes:
        """Pass."""
        try:
            kwargs["loaded"] = loaded = schema.load(data)
        except marshmallow.ValidationError as exc:
            raise ValidationError(
                schema=schema, exc=exc, api_endpoint=api_endpoint, obj=cls, data=data
            )
        except marshmallow_jsonapi.exceptions.IncorrectTypeError as exc:
            raise JsonApiError(
                schema=schema, exc=exc, api_endpoint=api_endpoint, obj=cls, data=data
            )

        cls._post_load_attrs(client=client, **kwargs)
        return loaded


class DataSchema(DataCommon, marshmallow.Schema):
    """Pass."""

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return dict

    @classmethod
    def _load_response(
        cls, data: ComplexTypes, client: Connect, api_endpoint: ApiEndpoint, **kwargs
    ) -> DataTypes:
        """Pass."""
        many = isinstance(data, (list, tuple))
        schema = cls(many=many)
        return cls._load_schema(schema=schema, data=data, client=client, api_endpoint=api_endpoint)

    @marshmallow.post_load
    def _post_load_process(self, data: ComplexTypes, **kwargs) -> DataTypes:
        """Pass."""
        model_cls = self._get_model_cls()
        data = data or {}
        if hasattr(model_cls, "from_dict"):
            obj = model_cls.from_dict(data)
        else:
            obj = model_cls(**data)
        return obj


class DataSchemaJson(DataSchema, marshmallow_jsonapi.Schema):
    """Pass."""

    id = marshmallow_jsonapi.fields.Str()
    document_meta = marshmallow_jsonapi.fields.DocumentMeta()

    class Meta:
        """Pass."""

        type_ = "base_schema"

    @classmethod
    def _load_response(
        cls, data: ComplexTypes, client: Connect, api_endpoint: ApiEndpoint, **kwargs
    ) -> DataTypes:
        """Pass."""
        cls._check_version(data=data, api_endpoint=api_endpoint)
        many = isinstance(data["data"], (list, tuple))
        schema = cls(many=many)
        return cls._load_schema(schema=schema, data=data, client=client, api_endpoint=api_endpoint)


@dataclasses.dataclass
class DataModel(dataclasses_json.DataClassJsonMixin, DataCommon):
    """Pass."""

    def replace_attrs(self, **kwargs) -> "DataModel":
        """Pass."""
        # TBD: does this do validation?
        return dataclasses.replace(self, **kwargs)

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return None

    @classmethod
    def _load_response(
        cls,
        data: ComplexTypes,
        client: Connect,
        api_endpoint: ApiEndpoint,
        schema_cls: Optional[Type[DataSchema]] = None,
        **kwargs,
    ) -> "DataModel":
        """Pass."""
        schema_cls = schema_cls or cls._get_schema_cls() or cls.schema
        many = isinstance(data, (list, tuple))
        schema = schema_cls(many=many)
        return cls._load_schema(schema=schema, data=data, client=client, api_endpoint=api_endpoint)

    @classmethod
    def _load_request(cls, api_endpoint: ApiEndpoint = None, client: Connect = None, **kwargs):
        """Pass."""
        schema = cls.schema()
        return cls._load_schema(
            schema=schema, data=kwargs, client=client, api_endpoint=api_endpoint
        )

    def _dump_request(
        self,
        schema_cls: Optional[Type[DataSchema]] = None,
        api_endpoint: ApiEndpoint = None,
        **kwargs,
    ) -> dict:
        """Pass."""
        schema_cls = schema_cls or self._get_schema_cls() or self.schema
        schema = schema_cls()
        dumped = self.to_dict()

        if isinstance(schema, DataSchemaJson) and "data" not in dumped:
            dumped = {"data": {"attributes": dumped, "type": schema.Meta.type_}}

        loaded = self._load_schema(
            schema=schema, data=dumped, client=None, api_endpoint=api_endpoint
        )
        redumped = schema.dump(loaded)
        return redumped

    def _dump_request_params(
        self,
        schema_cls: Optional[Type[DataSchema]] = None,
        api_endpoint: ApiEndpoint = None,
        **kwargs,
    ) -> Optional[dict]:
        """Pass."""
        dumped = self.to_dict()

        for k in list(dumped):
            if isinstance(dumped[k], dict):
                value = dumped.pop(k)
                for a, b in value.items():
                    dumped[f"{k}[{a}]"] = b
        return dumped

    def _dump_request_path(
        self, path: str, schema_cls: Optional[Type[DataSchema]] = None, api_endpoint=None, **kwargs
    ) -> str:
        """Pass."""
        format_args = {}
        format_args.update(self.to_dict())
        format_args.update(kwargs)
        path = path.format(**format_args)
        return path

    def __str__(self):
        """Pass."""
        props = self._to_str_properties()
        return self._str_join().join(props) if props else super().__str__()

    @staticmethod
    def _human_key(key: str) -> str:
        """Pass."""
        return key.replace("_", " ").title()

    @staticmethod
    def _str_join() -> str:
        """Pass."""
        return "\n"

    @staticmethod
    def _str_properties() -> List[str]:
        """Pass."""
        return []

    def _to_str_properties(self) -> List[str]:
        """Pass."""
        ret = []
        for prop in self._str_properties():
            key = self._human_key(prop)
            value = getattr(self, prop, None)
            if (
                isinstance(value, (list, tuple))
                and value
                and not all([isinstance(x, (str, int, bool, float, type(None))) for x in value])
            ):
                ret += [f"{key} #{idx}: {item}" for idx, item in enumerate(value)]
                continue
            ret.append(f"{key}: {value}")
        return ret

    @classmethod
    def _get_fields(cls) -> List[dataclasses.Field]:
        """Get a list of fields defined for current this dataclass object."""
        return dataclasses.fields(cls)
