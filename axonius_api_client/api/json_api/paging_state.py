# -*- coding: utf-8 -*-
"""API for working with adapters."""
import dataclasses
import datetime
import logging
import math
import time
import typing as t

from ...constants.api import MAX_PAGE_SIZE, PAGE_SIZE
from ...constants.logs import LOG_LEVEL_API
from ...exceptions import ApiError, StopFetch
from ...logs import get_obj_log
from ...tools import coerce_int, dt_now
from .base import BaseModel


@dataclasses.dataclass
class Page(BaseModel):
    """Pass."""

    state: "PagingState"
    method: callable
    request_obj: BaseModel

    response: t.ClassVar[t.Optional[t.List[BaseModel]]] = None
    start_date: t.ClassVar[t.Optional[datetime.datetime]] = None
    stop_date: t.ClassVar[t.Optional[datetime.datetime]] = None
    duration: t.ClassVar[t.Optional[datetime.timedelta]] = None
    page_number: t.ClassVar[int] = 0

    @staticmethod
    def get_model_cls() -> t.Any:
        """Pass."""
        return None

    def __post_init__(self):
        """Pass."""
        self.state.page_number += 1
        self.page_number = self.state.page_number
        self.state.page_history.append(self)
        self.state.check_stop()

        self.start_date = dt_now()
        self.state.log.debug(f"REQUESTING PAGE {self} for {self.state}")
        self.response = self.handle_response(response=self.get_response())
        self.stop_date = dt_now()
        self.duration = self.stop_date - self.start_date
        self.state.log.debug(f"RECEIVED PAGE {self} for {self.state}")

    def get_request_args(self) -> dict:
        """Pass."""
        request_obj = self.request_obj
        request_obj.page.offset = self.state.row_number
        request_obj.page.limit = self.state.page_size
        return {"request_obj": request_obj}

    def get_response(self) -> t.List[BaseModel]:
        """Pass."""
        return self.method(**self.get_request_args())

    def handle_response(self, response: t.List[BaseModel]) -> t.List[BaseModel]:
        """Pass."""
        if isinstance(response, (list, tuple)):
            self.state.rows_fetched_total += len(response)
        return response

    def __repr__(self):
        """Pass."""

        def getval(prop):
            value = getattr(self, prop, None)
            if value is not None and not isinstance(value, (str, int, float, bool)):
                value = str(value)
            return repr(value)

        props = [
            "start_date",
            "stop_date",
            "duration",
            "page_number",
            "row_count",
            "method",
        ]
        vals = ", ".join([f"{p}={getval(p)}" for p in props])
        return f"{self.__class__.__name__}({vals})"

    def __str__(self) -> t.List[str]:
        """Pass."""

        def getval(prop):
            value = getattr(self, prop, None)
            if value is not None and not isinstance(value, (str, int, float, bool)):
                value = str(value)
            return repr(value)

        props = [
            "duration",
            "page_number",
            "row_count",
        ]
        vals = ", ".join([f"{p}={getval(p)}" for p in props])
        return f"{self.__class__.__name__}({vals})"

    def check_stop(self):
        """Pass."""
        if not self.row_count:
            self.state.stop(reason="No rows returned")
        self.state.check_stop()

    def handle_sleep(self):
        """Pass."""
        time.sleep(self.state.page_sleep)

    def handle_row(self, row):
        """Pass."""
        self.state.row_number += 1
        self.state.rows_yielded_total += 1
        return row

    @property
    def rows(self) -> t.Generator[BaseModel, None, None]:
        """Pass."""
        self.check_stop()
        for row in self.response:
            yield self.handle_row(row=row)
            self.state.check_stop()

        self.handle_sleep()

    @property
    def row_count(self) -> t.Optional[int]:
        """Pass."""
        return len(self.response) if isinstance(self.response, (list, tuple)) else None


@dataclasses.dataclass
class PagingState(BaseModel):
    """Pass."""

    purpose: t.Optional[str] = None

    page_sleep: int = 0
    page_size: int = PAGE_SIZE

    row_start: int = 0
    row_stop: t.Optional[int] = None
    log_level: t.Union[int, str] = LOG_LEVEL_API
    page_cls: Page = Page

    page_number: t.ClassVar[int] = 0
    page_history: t.ClassVar[t.List[Page]] = None
    row_number: t.ClassVar[int] = 0
    rows_fetched_total: t.ClassVar[int] = 0
    rows_yielded_total: t.ClassVar[int] = 0

    start_date: t.ClassVar[t.Optional[datetime.datetime]] = None
    stop_date: t.ClassVar[t.Optional[datetime.datetime]] = None
    stop_reason: t.ClassVar[t.Optional[str]] = None
    stop_paging: t.ClassVar[bool] = False

    log: t.ClassVar[logging.Logger] = None

    def __post_init__(self):
        """Pass."""
        if not issubclass(self.page_cls, Page):
            raise ApiError(f"page_cls {self.page_cls} is not a subclass of {Page}")

        self.log: logging.Logger = get_obj_log(obj=self, level=self.log_level)
        self.page_sleep = coerce_int(obj=self.page_sleep, min_value=0, errmsg="error in page_sleep")
        self.page_size = coerce_int(
            obj=self.page_size, max_value=MAX_PAGE_SIZE, errmsg="error in page_size"
        )

        self.row_start = coerce_int(obj=self.row_start, min_value=0, errmsg="error in row_start")
        self.row_stop = coerce_int(
            obj=self.row_stop, min_value=0, allow_none=True, errmsg="error in row_stop"
        )
        self.page_history = []

        if isinstance(self.row_start, int) and self.row_start >= 1:
            self.row_number = self.row_start
            self.page_number = math.ceil(self.row_start / self.page_size)

        if isinstance(self.row_stop, int) and self.row_stop < self.page_size:
            self.page_size = self.row_stop

    def __enter__(self):
        """Pass."""
        self.start_date = dt_now()
        self.log.debug(f"STARTED: {self}")
        return self

    def __exit__(self, exc, value, traceback):
        """Pass."""
        if not self.stop_date:
            self.stop_date = dt_now()

        if not self.stop_reason:
            self.stop_reason = f"{self.__class__} exit"

        self.log.debug(f"STOPPED: {self}")

        if isinstance(value, StopFetch):
            return True

    def __repr__(self):
        """Pass."""
        return self.__str__()

    def __str__(self) -> t.List[str]:
        """Pass."""

        def getval(prop):
            value = getattr(self, prop, None)
            if (
                prop not in ["page_cls"]
                and value is not None
                and not isinstance(value, (str, int, float, bool))
            ):
                value = str(value)
            return repr(value)

        props = [
            "purpose",
            "duration",
            "start_date",
            "stop_date",
            "stop_reason",
            "stop_paging",
            "page_sleep",
            "page_size",
            "row_start",
            "row_stop",
            "page_number",
            "row_number",
            "rows_fetched_total",
            "page_cls",
        ]
        vals = ", ".join([f"{p}={getval(p)}" for p in props])
        return f"{self.__class__.__name__}({vals})"

    @property
    def duration(self) -> datetime.timedelta:
        """Pass."""
        now = dt_now()
        return (self.stop_date or now) - (self.start_date or now)

    def stop(self, reason: t.Optional[str] = None):
        """Pass."""
        self.stop_paging = True

        if reason:
            self.stop_reason = reason

        raise StopFetch(reason=reason, state=self)

    def check_stop(self):
        """Pass."""
        if isinstance(self.row_stop, int) and self.rows_yielded_total >= self.row_stop:
            self.stop(
                reason=f"rows_yielded_total {self.rows_yielded_total} >= row_stop {self.row_stop}",
            )
        if self.stop_paging:
            self.stop()

    def page(self, method: callable, request_obj: object) -> Page:
        """Pass."""
        return self.page_cls(state=self, method=method, request_obj=request_obj)
