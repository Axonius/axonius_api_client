# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import datetime
import math
import time
from typing import Generator, List, Optional, Union

from ...constants import MAX_PAGE_SIZE, PAGE_SIZE
from ...exceptions import ApiError, JsonError, NotFoundError
from ...tools import dt_now, dt_parse_tmpl, dt_sec_ago, json_dump, listify
from ..adapters import Adapters
from ..asset_callbacks import get_callbacks_cls
from ..mixins import ModelMixins
from .fields import Fields
from .labels import Labels
from .saved_query import SavedQuery


class AssetMixin(ModelMixins):
    """API model for working with user and device assets."""

    FIELD_TAGS: str = "labels"
    FIELD_AXON_ID: str = "internal_axon_id"
    FIELD_ADAPTERS: str = "adapters"
    FIELD_ADAPTER_LEN: str = "adapter_list_length"

    FIELDS_API: List[str] = [
        FIELD_AXON_ID,
        FIELD_ADAPTERS,
        FIELD_TAGS,
        FIELD_ADAPTER_LEN,
    ]

    @property
    def fields_default(self) -> List[dict]:
        """Fields to add to all get calls for this asset type.

        Returns:
            fields to add to
        """
        raise NotImplementedError  # pragma: no cover

    def destroy(self, destroy: bool, history: bool) -> dict:
        """Destroy ALL assets."""
        return self._destroy(destroy=destroy, history=history)

    def count(
        self, query: Optional[str] = None, history_date: Optional[str] = None
    ) -> int:
        """Get the count of assets.

        Args:
            query: default ``None`` -

                * if ``None`` return the count of all assets
                * if :obj:`str` return the count of assets that match a
                  query built by the GUI query wizard

        Returns:
            count of assets matching query
        """
        history_date = self.validate_history_date(value=history_date)
        return self._count(query=query, history_date=history_date)

    def count_by_saved_query(self, name: str, history_date: Optional[str] = None) -> int:
        """Get the count of assets that would be returned by a saved query.

        Args:
            name of saved query to get count of assets from

        Returns:
            count of assets matching query in saved query
        """
        sq = self.saved_query.get_by_name(value=name)
        history_date = self.validate_history_date(value=history_date)
        query = sq["view"]["query"]["filter"]
        return self._count(query=query, history_date=history_date)

    def get(
        self, generator: bool = False, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Get objects for a given query using paging.

        Args:
            generator: default ``False`` -

                * True: return an iterator for assets that will yield rows
                  as they are fetched
                * False: return a list of rows after all have been fetched
            **kwargs: passed to :meth:`get_generator`

        Yields:
            row if generator is True

        Returns:
            rows if generator is False
        """
        gen = self.get_generator(**kwargs)

        if generator:
            return gen

        return list(gen)

    def get_generator(
        self,
        query: Optional[str] = None,
        fields: Optional[Union[List[str], str]] = None,
        fields_manual: Optional[Union[List[str], str]] = None,
        fields_regex: Optional[Union[List[str], str]] = None,
        fields_default: bool = True,
        fields_root: Optional[str] = None,
        fields_map: Optional[dict] = None,
        max_rows: Optional[int] = None,
        max_pages: Optional[int] = None,
        row_start: int = 0,
        page_size: int = MAX_PAGE_SIZE,
        page_start: int = 0,
        page_sleep: int = 0,
        use_cursor: bool = True,
        export: Optional[str] = None,
        include_details: bool = False,
        sort_field: Optional[str] = None,
        sort_descending: bool = False,
        history_date: Optional[Union[str, datetime.datetime]] = None,
        **kwargs,
    ) -> Generator[dict, None, None]:
        """Get an iterator of objects for a given query using paging.

        Args:
            query (:obj:`str`, optional): default ``None`` -

                * if ``None`` return all assets
                * if :obj:`str` return the assets that match a query built
                  by the GUI query wizard
            fields (:obj:`list` of :obj:`str`, optional): default ``None`` -
                the fields to include for each asset, will be validated and
                processed into their fully qualified name using
                :meth:`Fields.validate`
            fields_manual (:obj:`list` of :obj:`str`, optional): default ``None`` -
                list of fully qualified fields to include for each asset
            fields_regex (:obj:`list` of :obj:`str`, optional): default ``None`` -
                list of fields to add using regular expression matches, will be
                validated and process into the matching fully qualified names using
                :meth:`Fields.validate`
            fields_default (:obj:`bool`, optional): default ``True`` -
                Include the fields in _default_fields
            fields_error (:obj:`bool`, optional): default ``True`` -
                throw an exception if fields fail to be validated by
                :meth:`Fields.validate`
            max_rows (:obj:`int`, optional): default ``None`` - return N assets
            max_pages (:obj:`int`, optional): default ``None`` - return N pages of assets
            page_size (:obj:`int`, optional):
                default default :data:`MAX_PAGE_SIZE` -
                return N assets per page
            page_start (:obj:`int`, optional): default ``0`` - start at page N

        Yields:
            :obj:`dict`: asset matching **query**
        """
        page_size = self._get_page_size(page_size=page_size, max_rows=max_rows)

        fields_map = fields_map or self.fields.get()

        fields = self.fields.validate(
            fields=fields,
            fields_manual=fields_manual,
            fields_regex=fields_regex,
            fields_default=fields_default,
            fields_map=fields_map,
            fields_root=fields_root,
        )

        if sort_field:
            sort_field = self.fields.get_field_name(
                value=sort_field, fields_map=fields_map
            )

        history_date = self.validate_history_date(value=history_date)

        store = {
            "query": query,
            "fields": fields,
            "include_details": include_details,
            "sort_field": sort_field,
            "sort_descending": sort_descending,
            "history_date": history_date,
        }

        state = {
            "max_pages": max_pages,
            "max_rows": max_rows,
            "use_cursor": use_cursor,
            "page_cursor": None,
            "page_sleep": page_sleep,
            "page_size": page_size,
            "page_number": page_start or 1,
            "page_start": page_start,
            "pages_to_fetch_left": None,
            "pages_to_fetch_total": None,
            "rows_to_fetch_left": None,
            "rows_to_fetch_total": None,
            "rows_fetched_this_page": None,
            "rows_fetched_total": page_start * page_size if page_start else row_start,
            "rows_processed_total": 0,
            "fetch_seconds_total": 0,
            "fetch_seconds_this_page": None,
            "stop_fetch": False,
            "stop_msg": None,
        }

        callbacks_cls = get_callbacks_cls(export=export)
        self._LAST_CALLBACKS = callbacks = callbacks_cls(
            apiobj=self, fields_map=fields_map, getargs=kwargs, state=state, store=store,
        )

        callbacks.start()

        self.LOG.info(f"STARTING FETCH store={json_dump(store)}")
        self.LOG.debug(f"STARTING FETCH state={json_dump(state)}")

        while not state["stop_fetch"]:
            if state["use_cursor"]:
                page = self._get_page_cursor(state=state, store=store)
            else:
                page = self._get_page_normal(state=state, store=store)

            rows = page.pop("assets")

            self.LOG.debug(f"FETCHED PAGE: {json_dump(page)}")
            self.LOG.debug(f"CURRENT PAGING STATE: {json_dump(state)}")

            if not rows:
                stop_msg = "no more rows returned"
                state["stop_fetch"] = True
                state["stop_msg"] = stop_msg
                self.LOG.debug(f"STOPPED FETCH: {stop_msg}")
                break

            for row in rows:
                row_items = callbacks.process_row(row=row)

                for row_item in listify(obj=row_items):
                    yield row_item

                if state["stop_fetch"]:
                    break

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
                state["stop_msg"] = stop_msg
                state["stop_fetch"] = True
                self.LOG.debug(f"STOPPED FETCH: {stop_msg}")
                break

            if state["use_cursor"]:
                state["page_number"] += 1

            time.sleep(state["page_sleep"])

        self.LOG.info(f"FINISHED FETCH store={store}")
        self.LOG.debug(f"FINISHED FETCH state={json_dump(state)}")

        callbacks.stop()

    def _get_page_cursor(self, state: dict, store: dict) -> dict:
        page_start_dt = dt_now()

        page = self._get_cursor(
            query=store["query"],
            fields=store["fields"],
            row_start=state["rows_fetched_total"],
            page_size=state["page_size"],
            cursor=state["page_cursor"],
            include_details=store["include_details"],
            sort_field=store["sort_field"],
            sort_descending=store["sort_descending"],
            history_date=store["history_date"],
        )

        state["fetch_seconds_this_page"] = dt_sec_ago(obj=page_start_dt, exact=True)
        state["fetch_seconds_total"] += state["fetch_seconds_this_page"]

        # only first page has totalResources with integer when cursor paging!!
        rows_to_fetch_total = page["page"]["totalResources"]

        if rows_to_fetch_total is not None:
            state["rows_to_fetch_total"] = rows_to_fetch_total

        state["rows_fetched_this_page"] = len(page["assets"])
        state["rows_fetched_total"] += state["rows_fetched_this_page"]
        state["rows_to_fetch_left"] = (
            state["rows_to_fetch_total"] - state["rows_fetched_total"]
        )
        state["pages_to_fetch_total"] = math.ceil(
            state["rows_to_fetch_total"] / state["page_size"]
        )
        state["pages_to_fetch_left"] = math.ceil(
            state["rows_to_fetch_left"] / state["page_size"]
        )

        state["page_cursor"] = page.get("cursor")
        return page

    def _get_page_normal(self, state: dict, store: dict) -> dict:
        page_start_dt = dt_now()

        page = self._get(
            query=store["query"],
            fields=store["fields"],
            row_start=state["rows_fetched_total"],
            page_size=state["page_size"],
            include_details=store["include_details"],
            sort_field=store["sort_field"],
            sort_descending=store["sort_descending"],
            history_date=store["history_date"],
        )

        state["fetch_seconds_this_page"] = dt_sec_ago(obj=page_start_dt, exact=True)
        state["fetch_seconds_total"] += state["fetch_seconds_this_page"]

        state["rows_to_fetch_total"] = page["page"]["totalResources"]
        state["rows_fetched_this_page"] = len(page["assets"])
        state["rows_fetched_total"] += state["rows_fetched_this_page"]
        state["rows_to_fetch_left"] = (
            state["rows_to_fetch_total"] - state["rows_fetched_total"]
        )
        state["page_number"] = page["page"]["number"]
        state["pages_to_fetch_total"] = page["page"]["totalPages"]
        state["pages_to_fetch_left"] = (
            state["pages_to_fetch_total"] - state["page_number"]
        )
        return page

    def get_by_id(self, id: str) -> dict:
        """Get the full metadata of all adapters for a single asset.

        Args:
            id (:obj:`str`): internal_axon_id of asset to get all metadata for

        Raises:
            :exc:`ValueNotFoundError`: if asset is not found with supplied **id**

        Returns:
            :obj:`dict`: dict with all metadata for all adapters for asset with
                **id** of internal_axon_id
        """
        try:
            return self._get_by_id(id=id)
        except JsonError:
            otype = self.router._object_type
            msg = f"Failed to find internal_axon_id {id!r} for {otype}"
            raise NotFoundError(msg)

    def get_by_saved_query(
        self, name: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Get assets that would be returned by a saved query.

        Args:
            name (:obj:`str`): name of saved query to get count of assets from
            **kwargs: passed to :meth:`get`

        Yields:
            :obj:`dict`: asset matching **query** if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: assets matching **query** if generator is False
        """
        sq = self.saved_query.get_by_name(value=name)
        kwargs["query"] = sq["view"]["query"]["filter"]
        kwargs["fields_manual"] = sq["view"]["fields"]
        kwargs.setdefault("fields_default", False)
        return self.get(**kwargs)

    def get_by_values(
        self,
        values: List[str],
        field: str,
        not_flag: bool = False,
        pre: str = "",
        post: str = "",
        field_manual: bool = False,
        fields_map: Optional[dict] = None,
        **kwargs,
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Pass."""
        if not field_manual:
            fields_map = fields_map or self.fields.get()

        field = self.fields.get_field_name(
            value=field, fields_map=fields_map, field_manual=field_manual
        )

        match = listify(values)
        match = [f"'{x.strip()}'" for x in match]
        match = ", ".join(match)

        inner = f"{field} in [{match}]"

        kwargs["query"] = self._build_query(
            inner=inner, pre=pre, post=post, not_flag=not_flag,
        )

        return self.get(fields_map=fields_map, **kwargs)

    def get_by_value_regex(
        self,
        value: str,
        field: str,
        cast_insensitive: bool = True,
        not_flag: bool = False,
        pre: str = "",
        post: str = "",
        field_manual: bool = False,
        fields_map: Optional[dict] = None,
        **kwargs,
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Pass."""
        if not field_manual:
            fields_map = fields_map or self.fields.get()

        field = self.fields.get_field_name(
            value=field, fields_map=fields_map, field_manual=field_manual
        )

        if cast_insensitive:
            inner = f'{field} == regex("{value}", "i")'
        else:
            inner = f'{field} == regex("{value}")'

        kwargs["query"] = self._build_query(
            inner=inner, pre=pre, post=post, not_flag=not_flag,
        )

        return self.get(fields_map=fields_map, **kwargs)

    def get_by_value(
        self,
        value: str,
        field: str,
        not_flag: bool = False,
        pre: str = "",
        post: str = "",
        field_manual: bool = False,
        fields_map: Optional[dict] = None,
        **kwargs,
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build query to get an asset by field value."""
        if not field_manual:
            fields_map = fields_map or self.fields.get()

        field = self.fields.get_field_name(
            value=field, fields_map=fields_map, field_manual=field_manual
        )

        inner = f'{field} == "{value}"'

        kwargs["query"] = self._build_query(
            inner=inner, pre=pre, post=post, not_flag=not_flag,
        )

        return self.get(fields_map=fields_map, **kwargs)

    def history_dates(self) -> dict:
        """Get all known historical dates for this asset type."""
        return self._history_dates()

    def validate_history_date(self, value: str) -> str:
        """Validate that a given date is known historical date."""
        if not value:
            return None

        dt = dt_parse_tmpl(obj=value)

        known_dates = self.history_dates()
        if dt not in known_dates:
            expl = "known history dates"
            known = "\n  " + "\n  ".join(list(known_dates))
            err = f"Unknown history date {dt!r}"
            msg = f"{err}, {expl}: {known}\n{err}, see above for {expl}"
            raise ApiError(msg)

        return known_dates[dt]

    def _build_query(
        self, inner: str, not_flag: bool = False, pre: str = "", post: str = ""
    ) -> str:
        """Pass."""
        if not_flag:
            inner = f"(not ({inner}))"
        else:
            inner = f"({inner})"

        lines = [pre, inner, post]
        query = " ".join([x.strip() for x in lines if x.strip()]).strip()

        self.LOG.debug(f"Built query: {query!r}")
        # XXX error if no OR / AND in pre & post
        return query

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        # cross reference
        self.adapters = Adapters(auth=self.auth, **kwargs)

        # children
        self.labels = Labels(parent=self)
        self.saved_query = SavedQuery(parent=self)
        self.fields = Fields(parent=self)

        super(AssetMixin, self)._init(**kwargs)

    def _count(
        self, query: Optional[str] = None, history_date: Optional[str] = None,
    ) -> int:
        """Direct API method to get the count of assets.

        Args:
            query (:obj:`str`, optional): default ``None`` -

                * if ``None`` return the count of all assets
                * if :obj:`str` return the count of assets that match a
                  query built by the GUI query wizard

        Returns:
            :obj:`int`: count of assets matching query
        """
        params = {}
        params["filter"] = query
        params["history"] = history_date
        return self.request(method="post", path=self.router.count, json=params)

    def _get(
        self,
        query: Optional[str] = None,
        fields: Optional[Union[List[str], str]] = None,
        row_start: int = 0,
        page_size: int = PAGE_SIZE,
        include_details: bool = False,
        history_date: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_descending: bool = False,
    ) -> dict:
        """Direct API method to get a page of assets.

        Args:
            query (:obj:`str`, optional): default ``None`` -

                * if ``None`` return all assets
                * if :obj:`str` return the assets that match a query built
                  by the GUI query wizard
            fields (:obj:`list` of :obj:`str` or :obj:`str`): default ``None`` -

                * if :obj:`str` CSV seperated list of fields (columns) to include in
                  return
                * if :obj:`list` of :obj:`str` the strs of fields (columns) to include
                  in return
            row_start (:obj:`int`, optional): default ``0`` - for paging, skip N rows
            page_size (:obj:`int`, optional): default ``0`` - for paging, return N rows

        Returns:
            :obj:`list` of :obj:`dict`: assets matching **query** with key/value pairs
                requested as per **fields**
        """
        page_size = self._get_page_size(page_size=page_size, max_rows=None)

        params = {}
        params["skip"] = row_start
        params["limit"] = page_size
        params["include_details"] = include_details
        params["history"] = history_date
        params["sort"] = sort_field
        params["desc"] = "1" if sort_descending else None
        params["filter"] = query

        if fields:
            if isinstance(fields, list):
                fields = ",".join(fields)

            params["fields"] = fields

        self._LAST_GET = params

        return self.request(method="post", path=self.router.root, json=params)

    def _get_cursor(
        self,
        query: Optional[str] = None,
        fields: Optional[Union[List[str], str]] = None,
        row_start: int = 0,
        page_size: int = PAGE_SIZE,
        cursor: Optional[str] = None,
        include_details: bool = False,
        history_date: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_descending: bool = False,
    ) -> dict:
        """Get a page for a given query."""
        page_size = self._get_page_size(page_size=page_size, max_rows=None)

        params = {}
        params["cursor"] = cursor
        params["skip"] = row_start
        params["limit"] = page_size
        params["include_details"] = include_details
        params["history"] = history_date
        params["sort"] = sort_field
        params["desc"] = "1" if sort_descending else None
        params["filter"] = query

        if fields:
            if isinstance(fields, list):
                fields = ",".join(fields)

            params["fields"] = fields

        self._LAST_GET = params

        return self.request(method="post", path=self.router.cached, json=params)

    def _get_by_id(self, id: str) -> dict:
        """Direct API method to get the full metadata of all adapters for a single asset.

        Args:
            id (:obj:`str`): internal_axon_id of asset to get all metadata for

        Returns:
            :obj:`dict`: dict with all metadata for all adapters for asset with
                **id** of internal_axon_id
        """
        path = self.router.by_id.format(id=id)
        return self.request(method="get", path=path)

    def _destroy(self, destroy: bool, history: bool) -> dict:
        """Destroy ALL assets."""
        data = {"destroy": destroy, "history": history}
        path = self.router.destroy
        return self.request(method="post", path=path, json=data)

    def _history_dates(self) -> dict:
        """Get all known historical dates for this asset type."""
        path = self.router.history_dates
        return self.request(method="get", path=path)
