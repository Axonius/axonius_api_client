# -*- coding: utf-8 -*-
"""API model base classes and mixins."""
import abc
import logging
import textwrap
import time
from typing import Any, Generator, List, Optional, Union

from .. import auth
from ..constants.api import MAX_PAGE_SIZE
from ..constants.logs import LOG_LEVEL_API, MAX_BODY_LEN
from ..exceptions import JsonError, JsonInvalid, NotFoundError, ResponseNotOk
from ..logs import get_obj_log
from ..tools import dt_now, dt_sec_ago, json_dump, json_load
from .routers import Router


class Model(metaclass=abc.ABCMeta):
    """API model base class."""

    @abc.abstractproperty
    def router(self) -> Router:
        """REST API routes definition for this API model."""
        raise NotImplementedError  # pragma: no cover


class PageSizeMixin:
    """Mixins for models that utilize paging in their endpoints."""

    def _get_page_size(
        self, page_size: Optional[int] = MAX_PAGE_SIZE, max_rows: Optional[int] = None
    ) -> int:
        if max_rows and max_rows < page_size:
            self.LOG.debug(f"CHANGED PAGE SIZE {page_size} to max_rows {max_rows}")
            page_size = max_rows

        if page_size > MAX_PAGE_SIZE or not page_size:
            self.LOG.debug(f"CHANGED PAGE SIZE {page_size} to max {MAX_PAGE_SIZE}")
            page_size = MAX_PAGE_SIZE

        return page_size


class ModelMixins(Model, PageSizeMixin):
    """Mixins for API Models."""

    def __init__(self, auth: auth.Model, **kwargs):
        """Mixins for API Models.

        Args:
            auth: object to use for auth and sending API requests
            **kwargs: passed to :meth:`_init`
        """
        log_level = kwargs.get("log_level", LOG_LEVEL_API)
        self.LOG: logging.Logger = get_obj_log(obj=self, level=log_level)
        """Logger for this object."""
        self.auth = auth
        """:obj:`axonius_api_client.auth.models.Mixins` authentication object."""
        self.http = auth.http
        """:obj:`axonius_api_client.http.Http` client to use to send requests,"""
        self._init(**kwargs)

        auth.check_login()

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        pass

    def __str__(self) -> str:
        """Show info for this model object."""
        cls = self.__class__
        auth = self.auth.__class__.__name__
        url = self.http.url
        return f"{cls.__module__}.{cls.__name__}(auth={auth!r}, url={url!r})"

    def __repr__(self) -> str:
        """Show info for this model object."""
        return self.__str__()

    def _build_err_msg(
        self,
        response,
        error: Optional[str] = None,
        exc: Optional[Exception] = None,
    ) -> str:
        """Build an error message from a response.

        Args:
            response (:obj:`requests.Response`): response that originated the error
            error: error message to include in exception
            exc: exception that was thrown if any
        """
        msgs = []

        url = response.url
        method = response.request.method
        code = response.status_code
        reason = response.reason
        out_len = len(response.request.body or "")
        in_len = len(response.text or "")

        msgs += [
            *([f"Original exception: {exc}"] if exc else []),
            "",
            f"URL: {url!r}, METHOD: {method}",
            f"CODE: {code!r}, REASON: {reason!r}, BYTES OUT: {out_len}, BYTES IN: {in_len}",
            "",
        ]

        response_obj = json_load(obj=response.text, error=False)

        if isinstance(response_obj, dict):
            msgs.append("Response Object:")
            for k, v in response_obj.items():
                msgs.append(
                    textwrap.fill(
                        str(v), initial_indent=f" - {k}: ", subsequent_indent="   ", width=80
                    )
                )

        else:
            msgs += ["Response Body:", str(response_obj)[:MAX_BODY_LEN]]

        error = error or "Error in REST API response"
        msgs = [error, *msgs, "", error]

        return "\n".join(msgs)

    def request(
        self,
        path: str,
        method: str = "get",
        raw: bool = False,
        is_json: bool = True,
        empty_ok: bool = False,
        error_status: bool = True,
        error_json_bad_status: bool = True,
        error_json_invalid: bool = True,
        **kwargs,
    ) -> Any:
        """Send a REST API request.

        Args:
            path: path to use in request
            method: method to use in request
            raw: return the raw response object
            is_json: return the response as deserialized json or just return the text body
            error_status: throw error if response has a bad status code
            error_json_bad_status: throw error if json response has non-empty error key
            error_json_invalid: throw error if response can not be deserialized into json
            **kwargs: Passed to :meth:`axonius_api_client.http.Http.__call__`

        Returns:
            :obj:`requests.Response` or :obj:`str` or :obj:`dict` or :obj:`int` or :obj:`list`
        """
        sargs = {}
        sargs.update(kwargs)
        sargs.update({"path": path, "method": method})

        response = self.http(**sargs)

        if raw:
            return response

        if empty_ok and not response.text:  # pragma: no cover
            return response.text

        if is_json and response.text:
            data = self._check_response_json(
                response=response,
                error_json_bad_status=error_json_bad_status,
                error_json_invalid=error_json_invalid,
            )
        else:
            data = response.text

        self._check_response_code(response=response, error_status=error_status)

        return data

    def _check_response_code(self, response, error_status: bool = True):
        """Check the status code of a response.

        Args:
            response: :obj:`requests.Response` object to check
            error_status: throw exc if response status code is bad

        Raises:
            :exc:`.ResponseNotOk`:
                if response has a status code that is an error and error_status is True
        """
        if error_status:
            try:
                response.raise_for_status()
            except Exception as exc:
                code = response.status_code
                respexc = ResponseNotOk(
                    self._build_err_msg(
                        response=response,
                        error=f"Response has a bad HTTP status code {code}",
                        exc=exc,
                    )
                )
                respexc.response = response
                respexc.exc = exc
                raise respexc

    def _check_response_json(
        self,
        response,
        error_json_bad_status: Optional[bool] = True,
        error_json_invalid: Optional[bool] = True,
        uses_api_response: Optional[bool] = False,
    ) -> Any:
        """Check the text body of a response is JSON.

        Args:
            response: :obj:`requests.Response` object to check
            error_json_bad_status: throw an exc if error key is not empty or status key == error
            error_json_invalid: throw an exc if response is invalid json

        Raises:
            :exc:`JsonInvalid`: if error_json_invalid is True and
                response has invalid json

            :exc:`JsonError`: if error_json_bad_status is True and
                response is a json dict that has a non-empty error key or a
                status key that == error
        """
        try:
            data = response.json()
        except Exception as exc:
            if error_json_invalid:
                respexc = JsonInvalid(
                    self._build_err_msg(
                        response=response, error="REST response object is not valid JSON", exc=exc
                    )
                )
                respexc.exc = exc
                respexc.response = response
                raise respexc

            return response.text

        if isinstance(data, dict):
            has_error = data.get("error")
            has_error_status = data.get("status") == "error"

            if (has_error or has_error_status) and error_json_bad_status:
                respexc = JsonError(
                    self._build_err_msg(
                        response=response, error="REST response object status key == error"
                    )
                )
                respexc.response = response
                raise respexc
        return data


class PagingMixinsObject(PageSizeMixin):
    """Mixins for API models that support object paging."""

    def get_by_uuid(self, value: str, **kwargs) -> dict:
        """Get an object by UUID.

        Args:
            value: uuid of object to get
            **kwargs: passed to :meth:`get`
        """
        rows = self.get(**kwargs)

        for row in rows:
            if row["uuid"] == value:
                return row

        tmpl = "name: {name!r}, uuid: {uuid!r}".format
        valid = "\n  " + "\n  ".join(sorted([tmpl(**row) for row in rows]))
        raise NotFoundError(f"uuid {value!r} not found, valid:{valid}")

    def get_by_name(self, value: str, **kwargs) -> dict:
        """Get an object by name.

        Args:
            value: name of object ot get
            **kwargs: passed to :meth:`get`
        """
        valid = []
        tmpl = "name: {name!r}".format
        for row in self.get(**kwargs):
            if row["name"] == value:
                return row
            valid.append(tmpl(**row))

        valid = "\n  " + "\n  ".join(sorted(valid))
        raise NotFoundError(f"name {value!r} not found, valid:{valid}")

    def get(
        self, generator: bool = False, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Get objects for a given query using paging.

        Args:
            generator: return an iterator for objects that will yield rows as they are fetched
            **kwargs: passed to :meth:`get_generator`
        """
        gen = self.get_generator(**kwargs)
        return gen if generator else list(gen)

    def get_generator(
        self,
        query: Optional[str] = None,
        max_rows: Optional[int] = None,
        max_pages: Optional[int] = None,
        page_size: int = MAX_PAGE_SIZE,
        page_start: int = 0,
        page_sleep: int = 0,
        **kwargs,
    ) -> Generator[dict, None, None]:
        """Get saved queries using paging.

        Args:
            query: mongo query to filter objects to return
            max_rows: only return N objects
            max_pages: only return N pages
            page_size: fetch N objects per page
            page_start: start at page N
            page_sleep: sleep for N seconds between each page fetch
        """
        page_size = self._get_page_size(page_size=page_size, max_rows=max_rows)

        store = {"query": query}

        state = {
            "max_pages": max_pages,
            "max_rows": max_rows,
            "page_sleep": page_sleep,
            "page_size": page_size,
            "page_number": page_start or 1,
            "row_to_fetch_next": page_start * page_size,
            "rows_fetched_this_page": None,
            "rows_processed_total": 0,
            "rows_fetched_total": 0,
            "fetch_seconds_total": 0,
            "fetch_seconds_this_page": 0,
            "stop_fetch": False,
            "stop_msg": None,
        }

        self.LOG.info(f"STARTING FETCH store={json_dump(store)}")
        self.LOG.debug(f"STARTING FETCH state={json_dump(state)}")

        while not state["stop_fetch"]:
            page_start = dt_now()
            page = self._get(
                query=store["query"],
                page_size=state["page_size"],
                row_start=state["row_to_fetch_next"],
            )
            page_took = dt_sec_ago(obj=page_start, exact=True)

            state["fetch_seconds_this_page"] = page_took
            state["fetch_seconds_total"] += state["fetch_seconds_this_page"]

            rows = page.pop("assets", [])
            state["rows_fetched_this_page"] = len(rows)
            state["rows_fetched_total"] += state["rows_fetched_this_page"]
            state["row_to_fetch_next"] += state["rows_fetched_this_page"]

            self.LOG.debug(f"FETCHED PAGE: {json_dump(page)}")
            self.LOG.debug(f"CURRENT PAGING STATE: {json_dump(state)}")

            if not rows:
                stop_msg = "no more rows returned"
                state["stop_fetch"] = True
                state["stop_msg"] = stop_msg
                self.LOG.debug(f"STOPPED FETCH: {stop_msg}")
                break

            for row in rows:
                yield row

                state["rows_processed_total"] += 1

                if state["max_rows"] and state["rows_processed_total"] >= state["max_rows"]:
                    stop_msg = "'rows_processed_total' greater than 'max_rows'"
                    state["stop_msg"] = stop_msg
                    state["stop_fetch"] = True
                    break

            if state["stop_fetch"]:
                stop_msg = state["stop_msg"]
                self.LOG.debug(f"STOPPED FETCH: {stop_msg}")
                break

            if state["max_pages"] and state["page_number"] >= state["max_pages"]:
                stop_msg = "'page_number' greater than 'max_pages'"
                state["stop_fetch"] = True
                state["stop_msg"] = stop_msg
                self.LOG.debug(f"STOPPED FETCH: {stop_msg}")
                break

            state["page_number"] += 1
            time.sleep(page_sleep)

        self.LOG.info(f"FINISHED FETCH store={json_dump(store)}")
        self.LOG.debug(f"FINISHED FETCH state={json_dump(state)}")


class ChildMixins:
    """Mixins model for API child objects."""

    def __init__(self, parent: Model):
        """Mixins model for API child objects.

        Args:
            parent: parent API model of this child
        """
        self.parent = parent
        self.http = parent.http
        self.auth = parent.auth
        self.router = parent.router
        self.request = parent.request
        self.LOG = parent.LOG.getChild(self.__class__.__name__)
        self._init(parent=parent)

    def _init(self, parent: Model):
        """Post init method for subclasses to use for extra setup.

        Args:
            parent: parent API model of this child
        """
        pass

    def __str__(self) -> str:
        """Show info for this model object."""
        return f"{self.__class__.__name__} for {self.parent}"

    def __repr__(self) -> str:
        """Show info for this model object."""
        return self.__str__()
