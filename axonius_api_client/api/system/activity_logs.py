# -*- coding: utf-8 -*-
"""API for working with product metadata."""
import dataclasses
import datetime
import re
import time
from typing import Generator, List, Optional, Union

from ...constants.api import PAGE_SIZE
from ...data import PropsData
from ...exceptions import ApiError
from ...tools import (coerce_int_float, dt_now, dt_parse, dt_sec_ago,
                      json_dump, listify, trim_float)
from ..mixins import ModelMixins, PageSizeMixin
from ..routers import API_VERSION, Router

SEARCH_PROPERTIES: List[str] = [
    "action",
    "category",
    "type",
    "message",
    "user",
]
PROPERTIES: List[str] = [
    "action",
    "category",
    "date",
    "hours_ago",
    "message",
    "type",
    "user",
]


@dataclasses.dataclass
class ActivityData(PropsData):
    """Pass."""

    raw: dict
    _str_join: str = ", "

    @property
    def _properties(self) -> List[str]:
        return PROPERTIES

    @property
    def _search_properties(self) -> List[str]:
        return SEARCH_PROPERTIES

    @property
    def action(self) -> str:
        """Pass."""
        return self.raw["action"]

    @property
    def category(self) -> str:
        """Pass."""
        return self.raw["category"]

    @property
    def type(self) -> str:
        """Pass."""
        return self.raw["type"]

    @property
    def date(self) -> datetime.datetime:
        """Pass."""
        return dt_parse(obj=self.raw["date"])

    @property
    def message(self) -> str:
        """Pass."""
        return self.raw["message"]

    @property
    def user(self) -> str:
        """Pass."""
        return self.raw["user"]

    @property
    def hours_ago(self) -> str:
        """Pass."""
        return trim_float(value=(dt_now() - self.date).total_seconds() / 60 / 60)

    def within_last_hours(self, hours: Optional[Union[int, float]] = None) -> bool:
        """Pass."""
        return coerce_int_float(value=hours) >= self.hours_ago if hours else True

    def within_dates(
        self,
        start: Optional[Union[str, datetime.datetime]] = None,
        end: Optional[Union[str, datetime.datetime]] = None,
    ) -> bool:
        """Pass."""
        start_match = True
        end_match = True

        if start:
            start = dt_parse(obj=start, default_tz_utc=True)
            start_match = self.date >= start

        if end:
            end = dt_parse(obj=end, default_tz_utc=True)
            end_match = end >= self.date

        return start_match and end_match

    def property_searches(self, **kwargs) -> bool:
        """Pass."""
        valid = self._search_properties

        all_searches = []
        hits = []
        for prop, searches in kwargs.items():
            if prop not in valid:
                err = f"Invalid property {prop!r}, must be one of {', '.join(valid)}"
                raise ApiError(err)

            searches = listify(searches)
            all_searches += searches

            value = getattr(self, prop) or ""

            if any([re.search(x, value, re.I) for x in searches]):
                hits.append({"propery": prop, "value": value})

        if hits or not all_searches:
            return True

        return False


class ActivityLogs(ModelMixins, PageSizeMixin):
    """API for working with activity logs.

    Examples:
        Pass

    """

    def get(
        self, generator: bool = False, **kwargs
    ) -> Union[Generator[ActivityData, None, None], List[ActivityData]]:
        """Get activity log entries.

        Args:
            generator: return an iterator for objects that will yield rows as they are fetched
            **kwargs: passed to :meth:`get_generator`
        """
        gen = self.get_generator(**kwargs)
        return gen if generator else list(gen)

    def get_generator(
        self,
        max_rows: Optional[int] = None,
        max_pages: Optional[int] = None,
        page_size: int = PAGE_SIZE,
        page_start: int = 0,
        page_sleep: int = 0,
        start_date: Optional[Union[str, datetime.datetime]] = None,
        end_date: Optional[Union[str, datetime.datetime]] = None,
        within_last_hours: Optional[int] = None,
        **kwargs,
    ) -> Generator[ActivityData, None, None]:
        """Get activity log entries.

        Args:
            max_rows: only return N objects
            max_pages: only return N pages
            page_size: fetch N objects per page
            page_start: start at page N
            page_sleep: sleep for N seconds between each page fetch
            start_date: only return records with dates after this value
            end_date: only return records with dates before this value
            within_last_hours: only return records that happened N hours ago
            **kwargs: only return records that regex match properties as keys
        """
        page_size = self._get_page_size(page_size=page_size, max_rows=max_rows)

        store = {}

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
            rows = self._get(
                page_size=state["page_size"],
                row_start=state["row_to_fetch_next"],
            )
            page_took = dt_sec_ago(obj=page_start, exact=True)

            state["fetch_seconds_this_page"] = page_took
            state["fetch_seconds_total"] += state["fetch_seconds_this_page"]

            state["rows_fetched_this_page"] = len(rows)
            state["rows_fetched_total"] += state["rows_fetched_this_page"]
            state["row_to_fetch_next"] += state["rows_fetched_this_page"]

            self.LOG.debug(f"CURRENT PAGING STATE: {json_dump(state)}")

            if not rows:
                stop_msg = "no more rows returned"
                state["stop_fetch"] = True
                state["stop_msg"] = stop_msg
                self.LOG.debug(f"STOPPED FETCH: {stop_msg}")
                break

            for row in rows:
                obj = ActivityData(raw=row)

                dt_match = obj.within_dates(start=start_date, end=end_date)
                hrs_match = obj.within_last_hours(hours=within_last_hours)
                props_match = obj.property_searches(**kwargs)

                if not all([dt_match, hrs_match, props_match]):
                    continue

                yield obj

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

    def _get(
        self,
        row_start: int = 0,
        page_size: int = PAGE_SIZE,
        search: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> dict:
        """Direct API method to get the activity logs."""
        data = {}
        data["skip"] = row_start
        data["limit"] = page_size
        data["search"] = search
        data["date_from"] = date_from
        data["date_to"] = date_to

        path = self.router.audit
        return self.request(method="get", path=path, params=data)

    @property
    def router(self) -> Router:
        """Router for this API model."""
        return API_VERSION.system
