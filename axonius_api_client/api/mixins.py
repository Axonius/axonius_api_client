# -*- coding: utf-8 -*-
"""API model base classes and mixins."""
import abc
import time

from ..constants import LOG_LEVEL_API, MAX_BODY_LEN, MAX_PAGE_SIZE
from ..exceptions import JsonError, JsonInvalid, NotFoundError, ResponseNotOk
from ..logs import get_obj_log
from ..tools import dt_now, dt_sec_ago, json_dump, json_load, json_reload


class Model:
    """API model base class."""

    @abc.abstractproperty
    def router(self):
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        raise NotImplementedError  # pragma: no cover


class PageSizeMixin:
    """Pass."""

    def _get_page_size(self, page_size=MAX_PAGE_SIZE, max_rows=None):
        if max_rows and max_rows < page_size:
            self.LOG.debug(f"CHANGED PAGE SIZE {page_size} to max_rows {max_rows}")
            page_size = max_rows

        if page_size > MAX_PAGE_SIZE:
            self.LOG.debug(f"CHANGED PAGE SIZE {page_size} to max {MAX_PAGE_SIZE}")
            page_size = MAX_PAGE_SIZE

        if not page_size:
            page_size = MAX_PAGE_SIZE

        return page_size


class ModelMixins(Model, PageSizeMixin):
    """Mixins for :obj:`Model` objects."""

    def __init__(self, auth, **kwargs):
        """Mixins for :obj:`Model` objects.

        Args:
            auth (:obj:`.auth.Model`): object to use for auth and sending API requests
            **kwargs: passed to :meth:`Mixins._init`
        """
        log_level = kwargs.get("log_level", LOG_LEVEL_API)
        self.LOG = get_obj_log(obj=self, level=log_level)
        """:obj:`logging.Logger`: Logger for this object."""

        self.auth = auth
        """:obj:`.auth.Model`: object to use for auth and sending API requests."""
        self.http = auth.http

        self._init(auth=auth, **kwargs)

        auth.check_login()

    def _init(self, auth, **kwargs):
        """Post init method for subclasses to use for extra setup.

        Args:
            auth (:obj:`.auth.Model`): object to use for auth and sending API requests
        """
        pass

    def __str__(self):
        """Show info for this model object."""
        cls = self.__class__
        auth = self.auth.__class__.__name__
        url = self.http.url
        return f"{cls.__module__}.{cls.__name__}(auth={auth!r}, url={url!r})"

    def __repr__(self):
        """Show info for this model object."""
        return self.__str__()

    def _get_page_size(self, page_size=MAX_PAGE_SIZE, max_rows=None):
        if max_rows and max_rows < page_size:
            self.LOG.debug(f"CHANGED PAGE SIZE {page_size} to max_rows {max_rows}")
            page_size = max_rows

        if page_size > MAX_PAGE_SIZE:
            self.LOG.debug(f"CHANGED PAGE SIZE {page_size} to max {MAX_PAGE_SIZE}")
            page_size = MAX_PAGE_SIZE

        if not page_size:
            page_size = MAX_PAGE_SIZE

        return page_size

    def _build_err_msg(self, response, error=None, exc=None):
        """Pass."""
        request_size = len(response.request.body or "")
        response_size = len(response.text or "")
        msgs = []
        msgs += [f"Original exception: {exc}"] if exc else []
        msgs += [
            "Request Body:",
            json_reload(obj=response.request.body, error=False, trim=MAX_BODY_LEN),
            "",
            "Response details:",
            f"  code: {response.status_code!r}",
            f"  reason: {response.reason!r}",
            f"  method={response.request.method!r}",
            f"  url: {response.url!r}",
            f"  request_size: {request_size}",
            f"  response_size: {response_size}",
        ]

        response_obj = json_load(obj=response.text, error=False)

        if isinstance(response_obj, dict):
            if "additional_data" in response_obj:
                msg = json_reload(obj=response_obj.pop("additional_data"), error=False)
                msgs += ["  ** Additional Data:", msg]

            if "status" in response_obj:
                msgs += ["  ** Status: " + response_obj.pop("status")]

            if "message" in response_obj:
                msgs += ["  ** Message: " + response_obj.pop("message")]

            msgs += [f"Extra: {response_obj}"] if response_obj else []
        else:
            msgs += ["Response Body:", response_obj]

        msgs += [error] if error else []

        return "\n" + "\n".join(msgs)

    def request(
        self,
        path,
        method="get",
        raw=False,
        is_json=True,
        error_status=True,
        error_json_bad_status=True,
        error_json_invalid=True,
        # fmt: off
        **kwargs
        # fmt: on
    ):
        """Send a REST API request using :attr:`.auth.Mixins.http`.

        Args:
            path (:obj:`str`): path to use in request
            method (:obj:`str`, optional): default ``get`` - method to use in request
            raw (:obj:`bool`, optional): default ``False`` -

                * if ``True`` return the raw :obj:`requests.Response` object
                * if ``False`` return the text or json of the response based on is_json
            is_json (:obj:`bool`, optional): default ``True`` - if raw is False:

                * if ``True`` return the decoded json of the response text body
                * if ``False`` return the text body of the response
            error_status (:obj:`bool`, optional): default ``True`` -

                * if ``True`` check response status code
                  with :meth:`_check_response_code`
                * if ``False`` do not check response status code
            **kwargs:
                Passed to :meth:`.http.Http.__call__`

        Returns:
            :obj:`requests.Response` or :obj:`object` or :obj:`str`:

                * :obj:`requests.Response`: if raw is True
                * :obj:`object`: if raw is False and is_json is True
                * :obj:`str`: if raw is False and is_json is False
        """
        sargs = {}
        sargs.update(kwargs)
        sargs.update({"path": path, "method": method})

        response = self.http(**sargs)

        if raw:
            return response

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

    def _check_response_code(self, response, error_status=True):
        """Check the status code of a response.

        Args:
            response (:obj:`requests.Response`): response object to check
            error_status (:obj:`bool`, optional): default ``True`` -

                * if ``True`` throw exc if response status code is bad
                * if ``False`` silently ignore bad response status codes

        Raises:
            :exc:`.ResponseNotOk`:
                if response has a status code that is an error and error_status is True
        """
        if error_status:
            try:
                response.raise_for_status()
            except Exception as exc:
                respexc = ResponseNotOk(
                    self._build_err_msg(
                        response=response,
                        error="Response has a bad status code!",
                        exc=exc,
                    )
                )
                respexc.exc = exc
                raise respexc

    def _check_response_json(
        self, response, error_json_bad_status=True, error_json_invalid=True
    ):
        """Check the text body of a response is JSON.

        Args:
            response (:obj:`requests.Response`): response object to check
            error_json_bad_status (:obj:`bool`, optional): default ``True`` -

                * if ``True`` throw an exc if response is a json dict that
                  has a non-empty error key or a status key that == error
                * if ``False`` ignore error and status keys in response json dicts
            error_json_invalid (:obj:`bool`, optional): default ``True`` -

                * if ``True`` throw an exc if response is invalid json
                * if ``False`` return the text of response if response is invalid json

        Raises:
            :exc:`.JsonInvalid`: if error_json_invalid is True and
                response has invalid json

            :exc:`.JsonError`: if error_json_bad_status is True and
                response is a json dict that has a non-empty error key or a
                status key that == error

        Returns:
            :obj:`object` or :obj:`str`:

                * :obj:`object` if response has json data
                * :obj:`str` if response has invalid json data
        """
        try:
            data = response.json()
        except Exception as exc:
            if error_json_invalid:
                respexc = JsonInvalid(
                    self._build_err_msg(
                        response=response, error="JSON is not valid in response", exc=exc
                    )
                )
                respexc.exc = exc
                raise respexc

            return response.text

        if isinstance(data, dict):
            has_error = data.get("error")
            has_error_status = data.get("status") == "error"

            if (has_error or has_error_status) and error_json_bad_status:
                respexc = JsonError(self._build_err_msg(response=response))
                raise respexc
        return data


class PagingMixinsObject(PageSizeMixin):
    """Pass."""

    def get_by_uuid(self, value, **kwargs):
        """Get a single saved query by name.

        Args:
            name (:obj:`str`): name of saved query to get
            **kwargs: passed to :meth:`get`

        Returns:
            :obj:`dict`: saved query
        """
        rows = self.get(**kwargs)

        for row in rows:
            if row["uuid"] == value:
                return row

        tmpl = "name: {name!r}, uuid: {uuid!r}".format
        valid = "\n  " + "\n  ".join(sorted([tmpl(**row) for row in rows]))
        raise NotFoundError(f"uuid {value!r} not found, valid:{valid}")

    def get_by_name(self, value, **kwargs):
        """Get a single saved query by name.

        Args:
            name (:obj:`str`): name of saved query to get
            **kwargs: passed to :meth:`get`

        Returns:
            :obj:`dict`: saved query
        """
        rows = self.get(**kwargs)

        for row in rows:
            if row["name"] == value:
                return row

        tmpl = "name: {name!r}".format
        valid = "\n  " + "\n  ".join(sorted([tmpl(**row) for row in rows]))
        raise NotFoundError(f"name {value!r} not found, valid:{valid}")

    def get(self, generator=False, **kwargs):
        """Get objects for a given query using paging.

        Args:
            generator (:obj:`bool`, optional): default ``False`` -

                * True: return an iterator for assets that will yield rows
                  as they are fetched
                * False: return a list of rows after all have been fetched
            **kwargs: passed to :meth:`get_generator`

        Yields:
            :obj:`dict`: row if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: rows if generator is False
        """
        gen = self.get_generator(**kwargs)

        if generator:
            return gen

        return list(gen)

    def get_generator(
        self,
        query=None,
        max_rows=None,
        max_pages=None,
        page_size=MAX_PAGE_SIZE,
        page_start=0,
        page_sleep=0,
        **kwargs,
    ):
        """Get saved queries using paging.

        Args:
            query (:obj:`str`, optional): default ``None`` - filter rows to return

                This is NOT a query built by the query wizard!
            page_size (:obj:`int`, optional): default ``0`` - for paging, return N rows
            max_rows (:obj:`int`, optional): default ``None`` - return N assets

        Returns:
            :obj:`list` of :obj:`dict`: list of saved query metadata
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

                if (
                    state["max_rows"]
                    and state["rows_processed_total"] >= state["max_rows"]
                ):
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
    """Mixins model for children of :obj:`Mixins`."""

    def __init__(self, parent):
        """Mixins model for children of :obj:`Model`.

        Args:
            parent (:obj:`Model`): parent API model of this child
        """
        self.parent = parent
        self.http = parent.http
        self.auth = parent.auth
        self.router = parent.router
        self.request = parent.request
        self.LOG = parent.LOG.getChild(self.__class__.__name__)
        self._init(parent=parent)

    def _init(self, parent):
        """Post init method for subclasses to use for extra setup.

        Args:
            parent (:obj:`Model`): parent API model of this child
        """
        pass

    def __str__(self):
        """Show info for this model object."""
        return f"{self.__class__.__name__} for {self.parent}"

    def __repr__(self):
        """Show info for this model object."""
        return self.__str__()
