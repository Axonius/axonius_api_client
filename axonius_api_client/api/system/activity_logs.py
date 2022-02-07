# -*- coding: utf-8 -*-
"""API for working with product metadata."""
import datetime
from typing import Generator, List, Optional, Union

from ...constants.api import MAX_PAGE_SIZE
from ...exceptions import StopFetch
from ...tools import json_dump
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ModelMixins


class ActivityLogs(ModelMixins):
    """API for working with activity logs.

    Examples:
        Pass

    """

    def get(
        self, generator: bool = False, **kwargs
    ) -> Union[
        Generator[json_api.audit_logs.AuditLog, None, None], List[json_api.audit_logs.AuditLog]
    ]:
        """Get activity log entries.

        Args:
            generator: return an iterator for objects that will yield rows as they are fetched
            **kwargs: passed to :meth:`get_generator`
        """
        gen = self.get_generator(**kwargs)
        return gen if generator else list(gen)

    def get_generator(
        self,
        start_date: Optional[Union[str, datetime.datetime]] = None,
        end_date: Optional[Union[str, datetime.datetime]] = None,
        within_last_hours: Optional[int] = None,
        max_rows: Optional[int] = None,
        **kwargs,
    ) -> Generator[json_api.audit_logs.AuditLog, None, None]:
        """Get activity log entries.

        Args:
            start_date: only return records with dates after this value
            end_date: only return records with dates before this value
            within_last_hours: only return records that happened N hours ago
            **kwargs: only return records that regex match properties as keys
        """
        state = {}
        state["total_rows_fetched"] = 0
        state["page_row_start"] = 0
        state["page_rows_fetched"] = None
        state["page_number"] = 1
        state["max_rows"] = max_rows
        state["start_date"] = start_date
        state["end_date"] = end_date
        state["within_last_hours"] = within_last_hours
        state["property_searches"] = kwargs

        while True:
            self.LOG.debug(f"Fetching page state={json_dump(state)}")
            try:
                rows = self._get(offset=state["page_row_start"])
                state["page_rows_fetched"] = len(rows)
                state["page_row_start"] += len(rows)
                state["page_number"] += 1

                if not rows:
                    raise StopFetch(reason="empty rows returned", state=state)

                for row in rows:
                    if (
                        isinstance(state["max_rows"], int)
                        and state["total_rows_fetched"] >= state["max_rows"]
                    ):
                        raise StopFetch(reason="reached max_rows", state=state)

                    state["total_rows_fetched"] += 1

                    if (
                        not row.within_dates(start=start_date, end=end_date)
                        or not row.within_last_hours(hours=within_last_hours)
                        or not row.property_searches(**kwargs)
                    ):
                        continue

                    yield row
            except StopFetch as exc:
                self.LOG.info(f"{type(exc)}(reason={exc}) -- state:\n{json_dump(exc.state)}")
                break

    def _get(
        self,
        offset: int = 0,
        limit: int = MAX_PAGE_SIZE,
        search: str = "",
        date_from: Optional[Union[str, datetime.datetime]] = None,
        date_to: Optional[Union[str, datetime.datetime]] = None,
    ) -> json_api.audit_logs.AuditLog:
        """Direct API method to get the activity logs."""
        api_endpoint = ApiEndpoints.audit_logs.get
        request_obj = api_endpoint.load_request(
            page={"limit": limit, "offset": offset},
            search=search,
            date_from=date_from,
            date_to=date_to,
        )
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)
