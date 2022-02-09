# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import inspect
import logging
from typing import List, Optional, Tuple, Type, Union

import requests

from ..constants.general import JSON_TYPES
from ..exceptions import (
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
from ..http import Http
from ..logs import get_obj_log
from ..tools import combo_dicts, get_cls_path, json_log
from .json_api.base import BaseModel, BaseSchema, BaseSchemaJson


def check_model_cls(obj: type, src: str):
    """Pass."""
    invalid = [BaseModel]
    if obj:
        if not inspect.isclass(obj) or obj in invalid or not issubclass(obj, BaseModel):
            raise ValueError(f"{src} {obj} must be a subclass of {BaseModel}")


def check_schema_cls(obj: type, src: str):
    """Pass."""
    invalid = [BaseSchema, BaseSchemaJson]
    if obj:
        if not inspect.isclass(obj) or obj in invalid or not issubclass(obj, BaseSchema):
            raise ValueError(f"{src} {obj} must be a subclass of {BaseSchema}")


@dataclasses.dataclass
class ApiEndpoint:
    """Container for defining an endpoints method, path, schemas, and models."""

    method: str
    """HTTP method to use for this endpoint."""

    path: str
    """Path to access endpoint, will be string formatted before request is made."""

    request_schema_cls: Optional[Type[Union[BaseSchema, BaseSchemaJson]]]
    """Class of marshmallow or marshmallow_json_api for validating request data."""

    request_model_cls: Optional[Type[BaseModel]]
    """Class of dataclass for containing request data."""

    response_schema_cls: Optional[Type[Union[BaseSchema, BaseSchemaJson]]]
    """Class of marshmallow or marshmallow_json_api class for validating response data."""

    response_model_cls: Optional[Type[BaseModel]]
    """Class of dataclass for containing response data."""

    http_args: dict = dataclasses.field(default_factory=dict)
    """Arguments to always pass to :meth:`Http.__call__` for this endpoint."""

    http_args_required: List[str] = dataclasses.field(default_factory=list)
    """Arguments that must always be supplied to :meth:`perform_request` as http_args={}."""

    request_as_none: bool = False
    """Do not serialize the request object when sending the request."""

    response_as_text: bool = False
    """Do not serialize the response object when receiving the response."""

    log_level: str = "debug"
    """Log level for this objects logger."""

    def __str__(self):
        """Get a pretty str for this object."""
        items = "\n  " + ",\n  ".join(self.str_properties) + ",\n"
        return f"{self.__class__.__name__}({items})"

    def __post_init__(self):
        """Pass."""
        for attr in ["request_model_cls", "response_model_cls"]:
            value = getattr(self, attr)
            check_model_cls(obj=value, src=attr)

        for attr in ["request_schema_cls", "response_schema_cls"]:
            value = getattr(self, attr)
            check_schema_cls(obj=value, src=attr)

    @property
    def str_properties(self) -> List[str]:
        """Get the properties for this endpoint as a list of strs."""
        return [
            f"method={self.method!r}",
            f"path={self.path!r}",
            f"request_schema={get_cls_path(self.request_schema_cls)}",
            f"request_model={get_cls_path(self.request_model_cls)}",
            f"response_schema={get_cls_path(self.response_schema_cls)}",
            f"response_model={get_cls_path(self.response_model_cls)}",
            f"request_as_none={self.request_as_none}",
            f"response_as_text={self.response_as_text}",
            f"http_args_required={self.http_args_required}",
        ]

    @property
    def log(self) -> logging.Logger:
        """Get the logger for this object."""
        return get_obj_log(obj=self, level=self.log_level)

    def perform_request(
        self, http: Http, request_obj: Optional[BaseModel] = None, raw: bool = False, **kwargs
    ) -> Union[BaseModel, JSON_TYPES]:
        """Perform a request to this endpoint using an http object.

        Args:
            http (Http): HTTP object to use to send request
            request_obj (Optional[BaseModel], optional): dataclass containing
                object to serialize for the request
            raw (bool): return the raw requests.Response object
            **kwargs: passed to :meth:`perform_request_raw` and :meth:`handle_response`

        Returns:
            Union[BaseModel, JSON_TYPES]: the data loaded from the response received
        """
        self.log.debug(f"{self!r} Performing request with request_obj type {type(request_obj)}")
        kwargs["response"] = response = self.perform_request_raw(
            http=http, request_obj=request_obj, **kwargs
        )
        return response if raw else self.handle_response(http=http, **kwargs)

    def perform_request_raw(
        self, http: Http, request_obj: Optional[BaseModel] = None, **kwargs
    ) -> Union[BaseModel, JSON_TYPES]:
        """Perform a request to this endpoint using an http object.

        Args:
            http (Http): HTTP object to use to send request
            request_obj (Optional[BaseModel], optional): dataclass containing
                object to serialize for the request
            **kwargs: passed to :meth:`get_http_args` and :meth:`Http.__call__`

        Returns:
            Union[BaseModel, JSON_TYPES]: the data loaded from the response received
        """
        http_args = self.get_http_args(request_obj=request_obj, **kwargs)
        response = http(**http_args)
        return response

    def load_request(self, **kwargs) -> Union[BaseModel, dict, None]:
        """Create a dataclass for a request_obj to send using :meth:`perform_request`.

        Args:
            **kwargs: passed to :meth:`BaseModel.load_request` if :attr:`request_model_cls`
                is set

        Returns:
            Union[BaseModel, dict, None]: Loaded dataclass object or dict of kwargs or None if
                kwargs empty
        """
        load_cls = self.request_load_cls
        ret = kwargs or None
        if load_cls:
            self.log.debug(f"{self!r} Loading request with load_cls {load_cls} kwargs {kwargs}")
            try:
                ret = load_cls.load_request(**kwargs)
            except Exception as exc:
                err = "Failed to load request object"
                details = [f"cls: {load_cls}", f"kwargs: {json_log(kwargs)}"]
                raise RequestLoadObjectError(api_endpoint=self, err=err, details=details, exc=exc)

            self.log.debug(f"{self!r} Loaded request into {load_cls}")
        return ret

    def load_response(
        self, data: dict, http: Http, unloaded: bool = False, **kwargs
    ) -> Union[BaseModel, JSON_TYPES]:
        """Load the response data into a dataclass model object.

        Args:
            data (dict): JSON data received from response
            http (Http): HTTP object used to receive response
            unloaded (bool): return the data without loading it into a dataclass model
            **kwargs: passed to :meth:`BaseSchema.load_response` or :meth:`BaseModel.load_response`

        Returns:
            Union[BaseModel, JSON_TYPES]: Loaded dataclass model or JSON data
        """
        if not unloaded:
            load_cls = self.response_load_cls
            if load_cls:
                self.log.debug(
                    f"{self!r} Loading response with data type {type(data)}, load_cls={load_cls}"
                )
                try:
                    data = load_cls.load_response(data=data, http=http, **kwargs)
                except Exception as exc:
                    err = "Failed to load response object"
                    details = [f"load_cls: {load_cls}"]
                    raise ResponseLoadObjectError(
                        api_endpoint=self, err=err, details=details, exc=exc
                    )

                self.log.debug(f"{self!r} Loaded response into {load_cls}")
        return data

    @property
    def request_load_cls(self) -> Optional[Union[Type[BaseSchema], Type[BaseModel]]]:
        """Get the class that should be used to load request data."""
        return self.request_model_cls or None

    @property
    def response_load_cls(self) -> Optional[Union[Type[BaseSchema], Type[BaseModel]]]:
        """Get the class that should be used to load response data."""
        return self.response_schema_cls or self.response_model_cls or None

    def handle_response(
        self, http: Http, response: requests.Response, **kwargs
    ) -> Union[BaseModel, JSON_TYPES]:
        """Get the response data.

        Args:
            http (Http): HTTP object used to receive response
            response (requests.Response): response to handle
            **kwargs: passed to :meth:`get_response_json` and :meth:`load_response`

        Returns:
            Union[BaseModel, JSON_TYPES]: Loaded dataclass model or JSON data

        """
        if self.response_as_text:
            data = response.text
            self.check_response_status(http=http, response=response, **kwargs)
        else:
            data = self.get_response_json(response=response)
            self.check_response_status(http=http, response=response, **kwargs)
            data = self.load_response(
                http=http, response=response, **combo_dicts(kwargs, data=data)
            )
        return data

    def get_response_json(self, response: requests.Response) -> JSON_TYPES:
        """Get the JSON from a response.

        Args:
            response (requests.Response): response to handle

        Raises:
            JsonInvalidError: if response can not be deserialized from JSON

        Returns:
            JSON_TYPES: deserialized JSON from response
        """
        try:
            data = response.json()
        except Exception as exc:
            raise JsonInvalidError(
                msg=f"Response has invalid JSON\nWhile in {self}", response=response, exc=exc
            )
        return data

    def check_response_status(
        self,
        http: Http,
        response: requests.Response,
        response_status_hook: Optional[callable] = None,
        **kwargs,
    ):
        """Check the status code of a response.

        Args:
            http (Http): HTTP object used to receive response
            response (requests.Response): response to handle
            response_status_hook (Optional[callable], optional): callable to perform
                extra checks of response status that takes args: http, response, kwargs
            **kwargs: Passed to `response_status_hook` if supplied, if hook returns truthy
                no more status checks are done

        Raises:
            InvalidCredentials: if response has has a 401 status code
            ResponseNotOk: if response has a bad status code
        """
        if callable(response_status_hook) and response_status_hook(
            http=http, response=response, **kwargs
        ):
            return

        msgs = [
            f"Response has a bad HTTP status code: {response.status_code}",
            f"While in {self}",
        ]

        if response.status_code == 401:
            msgs.append("Invalid credentials")
            raise InvalidCredentials(msg="\n".join(msgs), response=response)

        try:
            response.raise_for_status()
        except Exception as exc:
            raise ResponseNotOk(msg="\n".join(msgs), response=response, exc=exc)

    def get_http_args(
        self, request_obj: Optional[BaseModel] = None, http_args: Optional[dict] = None, **kwargs
    ) -> dict:
        """Build the arguments to supply to :meth:`Http.__call__`.

        Args:
            request_obj (Optional[BaseModel], optional): dataclass model to serialize for request
            http_args (Optional[dict], optional): Additional arguments to add
            **kwargs: passed to :meth:`dump_path` and :meth:`dump_object`

        Returns:
            dict: The arguments to make the request using :obj:`Http`.
        """
        self.check_request_obj(request_obj=request_obj)
        args = {}
        args["method"] = self.method
        args["path"] = self.dump_path(request_obj=request_obj, http_args=http_args, **kwargs)
        args.update(self.dump_object(request_obj=request_obj, **kwargs))
        args.update(self.http_args or {})
        args.update(http_args or {})
        self.check_missing_args(args=args)
        return args

    def _get_dump_object_method(
        self, request_obj: Optional[BaseModel] = None, **kwargs
    ) -> Tuple[str, callable]:
        """Get the method that should be used to dump a model and the arg for the request."""
        if self.method == "get" and callable(getattr(request_obj, "dump_request_params", None)):
            dump_method = request_obj.dump_request_params
            key = "params"
        elif callable(getattr(request_obj, "dump_request", None)):
            dump_method = request_obj.dump_request
            key = "json"
        else:
            err = f"Request object does not have dump_request methods: {request_obj!r}"
            details = [
                f"request_obj type: {type(request_obj)}",
                f"request_obj: {request_obj!r}",
            ]
            raise RequestFormatObjectError(api_endpoint=self, err=err, details=details)
        return key, dump_method

    def _call_dump_object_method(
        self, dump_method: callable, request_obj: Optional[BaseModel] = None, **kwargs
    ) -> dict:
        """Pass."""
        kwargs = combo_dicts(kwargs, schema_cls=self.request_schema_cls)
        try:
            return dump_method(**kwargs)
        except Exception as exc:
            err = f"Request formatting failed for object: {request_obj!r}"
            details = [
                f"dump_method: {dump_method}",
                f"kwargs: {json_log(kwargs)}",
                f"request_obj: {request_obj!r}",
            ]
            raise RequestFormatObjectError(api_endpoint=self, err=err, details=details, exc=exc)

    def dump_object(self, request_obj: Optional[BaseModel] = None, **kwargs) -> dict:
        """Serialize a dataclass model for a request.

        Args:
            request_obj (Optional[BaseModel], optional): dataclass model to serialize for request
            **kwargs: passed to :meth:`BaseModel.dump_request_params` if method is GET, else
                passed to :meth:`BaseModel.dump_request`

        Returns:
            dict: dict with 'json' or 'params' key to send to :meth:`Http.__call__`.

        Raises:
            RequestFormatObjectError: if dumping the request_obj fails
        """
        ret = {}
        if request_obj and not self.request_as_none:
            key, dump_method = self._get_dump_object_method(request_obj=request_obj, **kwargs)
            ret[key] = self._call_dump_object_method(
                dump_method=dump_method, request_obj=request_obj, **kwargs
            )
        return ret

    def dump_path(self, request_obj: Optional[BaseModel] = None, **kwargs) -> str:
        """Get the path to use for this endpoint.

        Args:
            request_obj (Optional[BaseModel], optional): dataclass model used as part
                of the string formatting for :attr:`path`
            **kwargs: Used as part of the string formatting for :attr:`path`

        Returns:
            str: formatted string of :attr:`path`
        """
        kwargs = combo_dicts(kwargs, {"path": self.path})

        if callable(getattr(request_obj, "dump_request_path", None)):
            method = request_obj.dump_request_path
        else:
            method = self.path.format

        try:
            return method(**kwargs)
        except Exception as exc:
            err = f"Request formatting failed for path: {self.path!r}"
            details = [
                f"method: {method}",
                f"kwargs: {json_log(kwargs)}",
                f"request_obj: {request_obj!r}",
            ]
            raise RequestFormatPathError(api_endpoint=self, err=err, details=details, exc=exc)

    def check_missing_args(self, args: dict):
        """Check for missing required arguments.

        Args:
            args (dict): arguments that will be supplied to :meth:`Http.__call__`

        Raises:
            RequestMissingArgsError: If args is missing one of :attr:`http_args_required`.
        """
        missing = [x for x in self.http_args_required if x not in args]
        if missing:
            err = f"Missing required HTTP arguments {missing!r}"
            details = ["HTTP arguments supplied: {json_log(args)}"]
            raise RequestMissingArgsError(api_endpoint=self, err=err, details=details)

    def check_request_obj(self, request_obj: BaseModel):
        """Check that the supplied request object is an instance of :attr:`request_model_cls`.

        Args:
            request_obj (BaseModel): request object to check

        Raises:
            RequestObjectTypeError: if request_obj is not an instance of :attr:`request_model_cls`
        """
        if self.request_model_cls and not isinstance(request_obj, self.request_model_cls):
            err = f"Request object must be of type {self.request_model_cls!r}"
            details = [
                f"Request object type supplied: {type(request_obj)}",
                f"Request object supplied: {request_obj!r}",
            ]
            raise RequestObjectTypeError(api_endpoint=self, err=err, details=details)
