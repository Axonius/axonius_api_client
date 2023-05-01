# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import inspect
import logging
import typing as t

import requests

from ..constants.general import JSON_TYPES, RERAISE
from ..constants.logs import LOG_LEVEL_ENDPOINTS
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
from ..logs import set_log_level
from ..tools import combo_dicts, get_cls_path, json_log
from .json_api.base import BaseModel, BaseSchema, BaseSchemaJson

LOGGER: logging.Logger = logging.getLogger(name=__name__)
set_log_level(obj=LOGGER, level=LOG_LEVEL_ENDPOINTS)


def check_mappings(endpoint: "ApiEndpoint"):
    """Check that the mappings for an endpoint are valid."""
    model_attrs: t.List[str] = ["request_model_cls", "response_model_cls"]
    schema_attrs: t.List[str] = ["request_schema_cls", "response_schema_cls"]

    for attr in model_attrs:
        value = getattr(endpoint, attr)
        check_model_cls(obj=value, src=attr)

    for attr in schema_attrs:
        value = getattr(endpoint, attr)
        check_schema_cls(obj=value, src=attr)


def check_model_cls(obj: type, src: str):
    """Check that supplied object is a subclass of BaseModel."""
    invalid = [BaseModel]
    if obj:
        if not inspect.isclass(obj) or obj in invalid or not issubclass(obj, BaseModel):
            raise ValueError(f"{src} {obj} must be a subclass of {BaseModel}")


def check_schema_cls(obj: type, src: str):
    """Check that supplied object is a subclass of BaseSchema."""
    invalid = [BaseSchema, BaseSchemaJson]
    if obj:
        if not inspect.isclass(obj) or obj in invalid or not issubclass(obj, BaseSchema):
            raise ValueError(f"{src} {obj} must be a subclass of {BaseSchema}")


@dataclasses.dataclass(eq=True, frozen=True)
class ApiEndpoint:
    """Container for defining an endpoints method, path, schemas, and models."""

    method: str
    """HTTP method to use for this endpoint."""

    path: str
    """Path to access endpoint, will be string formatted before request is made."""

    request_schema_cls: t.Optional[t.Type[t.Union[BaseSchema, BaseSchemaJson]]]
    """Class of marshmallow or marshmallow_json_api for validating request data."""

    request_model_cls: t.Optional[t.Type[BaseModel]]
    """Class of dataclass for containing request data."""

    response_schema_cls: t.Optional[t.Type[t.Union[BaseSchema, BaseSchemaJson]]]
    """Class of marshmallow or marshmallow_json_api class for validating response data."""

    response_model_cls: t.Optional[t.Type[BaseModel]]
    """Class of dataclass for containing response data."""

    http_args: dict = dataclasses.field(default_factory=dict)
    """Arguments to always pass to :meth:`Http.__call__` for this endpoint."""

    http_args_required: t.List[str] = dataclasses.field(default_factory=list)
    """Arguments that must always be supplied to :meth:`perform_request` as http_args={}."""

    request_as_none: bool = False
    """Do not serialize the request object when sending the request."""

    response_as_text: bool = False
    """Do not serialize the response object when receiving the response."""

    response_json_error: bool = True
    """Throw errors if the JSON can not be serialized."""
    log: t.ClassVar[logging.Logger] = LOGGER.getChild("ApiEndpoint")

    def __str__(self):
        """Get a pretty str for this object."""
        items = "\n  " + ",\n  ".join(self.str_properties) + ",\n"
        return f"{self.__class__.__name__}({items})"

    def __post_init__(self):
        """Dataclass post init."""
        super().__setattr__("log", LOGGER.getChild(self.__class__.__name__))
        check_mappings(endpoint=self)

    @property
    def str_properties(self) -> t.List[str]:
        """Get the properties for this endpoint as a list of strs."""
        return [
            f"method={self.method!r}, path={self.path!r}",
            f"request_schema={get_cls_path(self.request_schema_cls)}",
            f"request_model={get_cls_path(self.request_model_cls)}",
            f"response_schema={get_cls_path(self.response_schema_cls)}",
            f"response_model={get_cls_path(self.response_model_cls)}",
        ]

    def perform_request(
        self, http: Http, request_obj: t.Optional[BaseModel] = None, raw: bool = False, **kwargs
    ) -> t.Any:
        """Perform a request to this endpoint using a http object.

        Args:
            http (Http): HTTP object to use to send request
            request_obj (t.Optional[BaseModel], optional): dataclass containing
                object to serialize for the request
            raw (bool): return the raw requests.Response object
            **kwargs: passed to :meth:`perform_request_raw` and :meth:`handle_response`

        Returns:
            the data loaded from the response received
        """
        self.log.debug(f"{self!r} Performing request with request_obj type {type(request_obj)}")
        response: requests.Response = self.perform_request_raw(
            http=http, request_obj=request_obj, **kwargs
        )
        self.log.debug(f"{self!r} Received response {response}")
        kwargs["response"] = response
        return response if raw else self.handle_response(http=http, **kwargs)

    def perform_request_raw(
        self, http: Http, request_obj: t.Optional[BaseModel] = None, **kwargs
    ) -> requests.Response:
        """Perform a request to this endpoint using a http object.

        Args:
            http (Http): HTTP object to use to send request
            request_obj (t.Optional[BaseModel], optional): dataclass containing
                object to serialize for the request
            **kwargs: passed to :meth:`get_http_args` and :meth:`Http.__call__`

        Returns:
            requests.Response: the response received
        """
        return http(**self.get_http_args(request_obj=request_obj, **kwargs))

    def load_request(
        self,
        remove_unknown_arguments: bool = False,
        warn_unknown_arguments: bool = False,
        reraise: bool = RERAISE,
        **kwargs,
    ) -> t.Any:
        """Create a dataclass for a request_obj to send using :meth:`perform_request`.

        Args:
            remove_unknown_arguments (bool, optional): remove unknown arguments from kwargs
            warn_unknown_arguments (bool, optional): warn about unknown arguments in kwargs
            reraise (bool, optional): reraise exceptions
            **kwargs: passed to :meth:`BaseModel.load_request` if :attr:`request_model_cls`
                is set

        Returns:
            t.Union[BaseModel, dict, None]: Loaded dataclass object or dict of kwargs or None if
                kwargs empty
        """
        load_cls = self.request_load_cls

        ret = kwargs or None
        if load_cls:
            args_cleaner = getattr(load_cls, "remove_unknown_arguments", False)
            if callable(args_cleaner):
                kwargs, _ = args_cleaner(
                    kwargs=kwargs,
                    remove_unknown_arguments=remove_unknown_arguments,
                    warn_unknown_arguments=warn_unknown_arguments,
                )
            self.log.debug(f"{self!r} Loading request with load_cls {load_cls} kwargs {kwargs}")
            try:
                ret = load_cls.load_request(**kwargs)
            except Exception as exc:
                if reraise:
                    raise
                err = "Failed to load request object"
                details = [f"cls: {load_cls}", f"kwargs: {json_log(kwargs)}"]
                raise RequestLoadObjectError(api_endpoint=self, err=err, details=details, exc=exc)

            self.log.debug(f"{self!r} Loaded request into {load_cls}")
        return ret

    def load_response(
        self, data: dict, http: Http, unloaded: bool = False, **kwargs
    ) -> t.Union[BaseModel, JSON_TYPES]:
        """Load the response data into a dataclass model object.

        Args:
            data (dict): JSON data received from response
            http (Http): HTTP object used to receive response
            unloaded (bool): return the data without loading it into a dataclass model
            **kwargs: passed to :meth:`BaseSchema.load_response` or :meth:`BaseModel.load_response`

        Returns:
            t.Union[BaseModel, JSON_TYPES]: Loaded dataclass model or JSON data
        """
        kwargs["reraise"] = kwargs.get("reraise", RERAISE)

        if not unloaded:
            load_cls = self.response_load_cls
            if load_cls:
                self.log.debug(
                    f"{self!r} Loading response with data type {type(data)}, load_cls={load_cls}"
                )
                try:
                    data = load_cls.load_response(data=data, http=http, **kwargs)
                except Exception as exc:
                    if kwargs["reraise"]:
                        raise
                    err = "Failed to load response object"
                    details = [f"load_cls: {load_cls}"]
                    raise ResponseLoadObjectError(
                        api_endpoint=self, err=err, details=details, exc=exc
                    )

                self.log.debug(f"{self!r} Loaded response into {load_cls}")
        return data

    @property
    def request_load_cls(self) -> t.Optional[t.Union[t.Type[BaseSchema], t.Type[BaseModel]]]:
        """Get the class that should be used to load request data."""
        return self.request_model_cls or None

    @property
    def response_load_cls(self) -> t.Optional[t.Union[t.Type[BaseSchema], t.Type[BaseModel]]]:
        """Get the class that should be used to load response data."""
        return self.response_schema_cls or self.response_model_cls or None

    def handle_response(
        self, http: Http, response: requests.Response, **kwargs
    ) -> t.Union[BaseModel, JSON_TYPES]:
        """Get the response data.

        Args:
            http (Http): HTTP object used to receive `response`
            response (requests.Response): response to handle
            **kwargs: passed to :meth:`get_response_json` and :meth:`load_response`

        Returns:
            t.Union[BaseModel, JSON_TYPES]: Loaded dataclass model or JSON data

        """
        if self.response_as_text:
            data = response.text
            self.check_response_status(http=http, response=response, **kwargs)
        else:
            data = self.get_response_json(response=response, **kwargs)
            self.check_response_status(http=http, response=response, **kwargs)
            data = self.load_response(
                http=http, response=response, **combo_dicts(kwargs, data=data)
            )
            # noinspection PyBroadException
            try:
                setattr(data, "RESPONSE", response)
            except Exception:
                pass
        return data

    def get_response_json(self, response: requests.Response, **kwargs) -> JSON_TYPES:
        """Get the JSON from a response.

        Args:
            response (requests.Response): response to handle

        Raises:
            JsonInvalidError: if response can not be deserialized from JSON

        Returns:
            JSON_TYPES: deserialized JSON from response
        """
        reraise = kwargs.get("reraise", RERAISE)

        try:
            return response.json()
        except Exception as exc:
            if reraise:
                raise
            msg = f"Response has invalid JSON\nWhile in {self}"
            if self.response_json_error:
                raise JsonInvalidError(msg=msg, response=response, exc=exc)
            return response.text

    def check_response_status(
        self,
        http: Http,
        response: requests.Response,
        response_status_hook: t.Optional[callable] = None,
        **kwargs,
    ):
        """Check the status code of a response.

        Args:
            http (Http): HTTP object used to receive `response`
            response (requests.Response): response to handle
            response_status_hook (t.Optional[callable], optional): callable to perform
                extra checks of response status that takes args: http, response, kwargs
            **kwargs: Passed to `response_status_hook` if supplied, if hook returns truthy
                no more status checks are done

        Notes:
            If response_status_hook returns True, the rest of the check_response_status
            workflow will be skipped

        Raises:
            InvalidCredentials: if response has a 401 status code
            ResponseNotOk: if response has a bad status code
        """
        kwargs.setdefault("reraise", RERAISE)

        if callable(response_status_hook):
            hook_ret = response_status_hook(http=http, response=response, **kwargs)
            if hook_ret is True:
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
            if kwargs["reraise"]:
                raise
            raise ResponseNotOk(msg="\n".join(msgs), response=response, exc=exc)

    def get_http_args(
        self,
        request_obj: t.Optional[BaseModel] = None,
        http_args: t.Optional[dict] = None,
        **kwargs,
    ) -> dict:
        """Build the arguments to supply to :meth:`Http.__call__`.

        Args:
            request_obj (t.Optional[BaseModel], optional): dataclass model to serialize for request
            http_args (t.Optional[dict], optional): Additional arguments to add
            **kwargs: passed to :meth:`dump_path` and :meth:`dump_object`

        Returns:
            dict: The arguments to make the request using :obj:`Http`.
        """
        self.check_request_obj(request_obj=request_obj)
        data_args: dict = self.dump_object(request_obj=request_obj, **kwargs)
        path: str = self.dump_path(request_obj=request_obj, http_args=http_args, **kwargs)
        base_args: dict = dict(path=path, method=self.method)
        args: dict = combo_dicts(self.http_args, data_args, base_args, http_args)
        self.check_missing_args(args=args)
        return args

    def dump_object(self, request_obj: t.Any = None, **kwargs) -> dict:
        """Dump a request object to a python object.

        Args:
            request_obj (t.Any, optional): dataclass model to serialize for request
            **kwargs: passed to dump_method

        Returns:
            dict: dict with 'json' or 'params' keys to send to :meth:`Http.__call__`.
        """
        data: dict = {}
        if request_obj and not self.request_as_none:
            data_key, dump_method = self._get_dump_method(request_obj=request_obj)
            data[data_key] = self._call_dump_method(
                **combo_dicts(kwargs, dump_method=dump_method, request_obj=request_obj)
            )
        return data

    # noinspection PyUnusedLocal
    def _get_dump_method(
        self, request_obj: t.Optional[BaseModel] = None
    ) -> t.Tuple[str, t.Optional[callable]]:
        """Get the method that should be used to dump a model and the arg for the request."""
        dump_get: t.Optional[callable] = getattr(request_obj, "dump_request_params", None)
        dump_post: t.Optional[callable] = getattr(request_obj, "dump_request", None)
        key: str = ""
        dump_method: t.Optional[callable] = None
        if self.method == "get" and callable(dump_get):
            dump_method = dump_get
            key = "params"
        elif callable(dump_post):
            dump_method = dump_post
            key = "json"
        elif request_obj:
            err = f"Request object does not have dump_request methods: {request_obj!r}"
            details = [
                f"request_obj type: {type(request_obj)}",
                f"request_obj: {request_obj!r}",
            ]
            raise RequestFormatObjectError(api_endpoint=self, err=err, details=details)
        return key, dump_method

    def _call_dump_method(
        self, dump_method: callable, request_obj: t.Optional[BaseModel] = None, **kwargs
    ) -> dict:
        """Pass."""
        kwargs.setdefault("reraise", RERAISE)
        kwargs.setdefault("schema_cls", self.request_schema_cls)

        try:
            return dump_method(**kwargs)
        except Exception as exc:
            if kwargs["reraise"]:
                raise
            err = f"Request formatting failed for object: {request_obj!r}"
            details = [
                f"dump_method: {dump_method}",
                f"kwargs: {json_log(kwargs)}",
                f"request_obj: {request_obj!r}",
            ]
            raise RequestFormatObjectError(api_endpoint=self, err=err, details=details, exc=exc)

    def dump_path(self, request_obj: t.Optional[BaseModel] = None, **kwargs) -> str:
        """Get the path to use for this endpoint.

        Args:
            request_obj (t.Optional[BaseModel], optional): dataclass model used as part
                of the string formatting for :attr:`path`
            **kwargs: Used as part of the string formatting for :attr:`path`

        Returns:
            str: formatted string of :attr:`path`
        """
        kwargs.setdefault("path", self.path)
        kwargs.setdefault("reraise", RERAISE)

        cls_dump = getattr(request_obj, "dump_request_path", None)
        method = cls_dump if callable(cls_dump) else self.path.format

        try:
            return method(**kwargs)
        except Exception as exc:
            if kwargs["reraise"]:
                raise
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
        if self.request_model_cls and not self.request_as_none:
            if not isinstance(request_obj, self.request_model_cls):
                err = f"Request object must be of type {self.request_model_cls!r}"
                details = [
                    f"Request object type supplied: {type(request_obj)}",
                    f"Request object supplied: {request_obj!r}",
                ]
                raise RequestObjectTypeError(api_endpoint=self, err=err, details=details)
