# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import logging
from typing import List, Optional, Union

from ..exceptions import ApiError, InvalidCredentials, JsonInvalid, ResponseNotOk
from ..http import Http
from ..logs import get_obj_log
from ..tools import combo_dicts, json_reload
from . import json_api


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
        http: Http,
        request_obj: Optional[json_api.base.BaseModel] = None,
        **kwargs,
    ) -> Union[dict, json_api.base.BaseModel]:
        """Pass."""
        kwargs["response"] = self.perform_request_raw(http=http, request_obj=request_obj, **kwargs)
        return self.handle_response(http=http, **kwargs)

    def perform_request_raw(
        self,
        http: Http,
        request_obj: Optional[json_api.base.BaseModel] = None,
        **kwargs,
    ):
        """Pass."""
        http_args = self.get_http_args(request_obj=request_obj, **kwargs)
        response = http(**http_args)
        return response

    def load_request(self, **kwargs) -> Optional[Union[json_api.base.BaseModel, dict]]:
        """Pass."""
        if self.request_model_cls:
            this_kwargs = {"api_endpoint": self}
            this_kwargs = combo_dicts(kwargs, this_kwargs)
            return self.request_model_cls.load_request(**this_kwargs)
        return kwargs or None

    def load_response(
        self, data: dict, http: Http, **kwargs
    ) -> Union[json_api.base.BaseModel, dict]:
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
            data = use.load_response(data=data, http=http, **this_kwargs)

        return data

    def handle_response(
        self, http: Http, response, **kwargs
    ) -> Union[str, json_api.base.BaseModel, dict]:
        """Pass."""
        if self.response_as_text:
            self.handle_response_status(http=http, response=response, **kwargs)
            return response.text

        data = self.handle_response_json(http=http, response=response, **kwargs)

        this_kwargs = {"data": data}
        this_kwargs = combo_dicts(kwargs, this_kwargs)

        self.handle_response_status(http=http, response=response, **this_kwargs)

        return self.load_response(http=http, response=response, **this_kwargs)

    def handle_response_json(self, http: Http, response, **kwargs) -> dict:
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

    def handle_response_status(self, http: Http, response, **kwargs):
        """Check the status code of a response.

        Args:
            response: :obj:`requests.Response` object to check

        Raises:
            :exc:`.InvalidCredentials`: if response has has a 401 status code
            :exc:`.ResponseNotOk`: if response has a bad status code
        """
        hook = kwargs.get("response_status_hook")

        if callable(hook):
            hook(http=http, response=response, **kwargs)

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
        request_obj: Optional[json_api.base.BaseModel] = None,
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
            args["path"] = request_obj.dump_request_path(**this_kwargs)

            if not self.request_as_none:
                this_kwargs = {"api_endpoint": self, "schema_cls": self.request_schema_cls}
                this_kwargs = combo_dicts(kwargs, this_kwargs)

                if self.method == "get":
                    args["params"] = request_obj.dump_request_params(**this_kwargs)
                else:
                    args["json"] = request_obj.dump_request(**this_kwargs)

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

    def check_request_obj(self, request_obj: json_api.base.BaseModel):
        """Pass."""
        model_check = self.request_model_cls
        if model_check and not isinstance(request_obj, model_check):
            otype = type(request_obj)
            msg = f"Request object must be of type {model_check!r}, not of type {otype!r}"
            raise ApiError(msg)
