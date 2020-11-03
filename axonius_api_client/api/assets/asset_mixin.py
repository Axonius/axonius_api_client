# -*- coding: utf-8 -*-
"""API model mixin for device and user assets."""
import math
import time
from datetime import datetime, timedelta
from typing import Generator, List, Optional, Union

from ...constants.api import DEFAULT_CALLBACKS_CLS, MAX_PAGE_SIZE, PAGE_SIZE
from ...exceptions import ApiError, JsonError, NotFoundError
from ...tools import dt_now, dt_parse_tmpl, dt_sec_ago, json_dump, listify
from ..asset_callbacks.tools import get_callbacks_cls
from ..mixins import ModelMixins
from ..wizards import Wizard, WizardCsv, WizardText


class AssetMixin(ModelMixins):
    """API model mixin for device and user assets.

    Examples:
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
        ``apiobj`` is either ``client.devices`` or ``client.users``

        >>> apiobj = client.devices  # or client.users

        * Get count of assets: :meth:`count`
        * Get count of assets from a saved query: :meth:`count_by_saved_query`
        * Get assets: :meth:`get`
        * Get assets from a saved query: :meth:`get_by_saved_query`
        * Get the full data set for a single asset: :meth:`get_by_id`
        * Work with saved queries: :obj:`axonius_api_client.api.assets.saved_query.SavedQuery`
        * Work with fields: :obj:`axonius_api_client.api.assets.fields.Fields`
        * Work with tags: :obj:`axonius_api_client.api.assets.labels.Labels`

    See Also:
        This object is not usable directly, it only stores the logic that is common for working
        with device and user assets:

        * Device assets :obj:`axonius_api_client.api.assets.devices.Devices`
        * User assets :obj:`axonius_api_client.api.assets.users.Users`

    """

    def count(
        self,
        query: Optional[str] = None,
        history_date: Optional[Union[str, timedelta, datetime]] = None,
        wiz_entries: Optional[List[dict]] = None,
    ) -> int:
        """Get the count of assets from a query.

        Examples:
            Get count of all assets

            >>> count = apiobj.count()

            Get count of all assets for a given date

            >>> count = apiobj.count(history_date="2020-09-29")

            Get count of assets matching a query built by the GUI query wizard

            >>> query='(specific_data.data.name == "test")'
            >>> count = apiobj.count(query=query)

            Get count of assets matching a query built by the API client query wizard

            >>> entries = [{'type': 'simple', 'value': 'name equals test'}]
            >>> count = apiobj.count(wiz_entries=entries)

        Args:
            query: if supplied, only return the count of assets that match the query
                if not supplied, the count of all assets will be returned
            history_date: return asset count for a given historical date
            wiz_entries: wizard expressions to create query from

        """
        query = self.wizard.parse(entries=wiz_entries)["query"] if wiz_entries else query
        history_date = self.validate_history_date(value=history_date)
        return self._count(query=query, history_date=history_date)

    def count_by_saved_query(
        self, name: str, history_date: Optional[Union[str, timedelta, datetime]] = None
    ) -> int:
        """Get the count of assets for a query defined in a saved query.

        Examples:
            Get count of assets returned from a saved query

            >>> count = apiobj.count_by_saved_query(name="test")

            Get count of assets returned from a saved query for a given date

            >>> count = apiobj.count_by_saved_query(name="test", history_date="2020-09-29")

        Args:
            name: saved query to get count of assets from
            history_date: return count for a given historical date
        """
        sq = self.saved_query.get_by_name(value=name)
        history_date = self.validate_history_date(value=history_date)
        query = sq["view"]["query"]["filter"]
        return self._count(query=query, history_date=history_date)

    def get(
        self, generator: bool = False, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        r"""Get assets from a query.

        Examples:
            Get all assets with the default fields defined in the API client

            >>> assets = apiobj.get()

            Get all assets using an iterator

            >>> assets = [x for x in apiobj.get(generator=True)]

            Get all assets with fields that equal names

            >>> assets = apiobj.get(fields=["os.type", "aws:aws_device_type"])

            Get all assets with fields that fuzzy match names and no default fields

            >>> assets = apiobj.get(fields_fuzzy=["last", "os"], fields_default=False)

            Get all assets with fields that regex match names a

            >>> assets = apiobj.get(fields_regex=["^os\."])

            Get all assets with all root fields for an adapter

            >>> assets = apiobj.get(fields_root="aws")

            Get all assets for a given date in history and sort the rows on a field

            >>> assets = apiobj.get(history_date="2020-09-29", sort_field="name")

            Get all assets with details of which adapter connection provided the agg data

            >>> assets = apiobj.get(include_details=True)

            Get assets matching a query built by the GUI query wizard

            >>> query='(specific_data.data.name == "test")'
            >>> assets = apiobj.get(query=query)

            Get assets matching a query built by the API client query wizard

            >>> entries=[{'type': 'simple', 'value': 'name equals test'}]
            >>> assets = apiobj.get(wiz_entries=entries)

        See Also:
            This method is used by all other get* methods under the hood and their kwargs are
            passed thru to this method and passed to :meth:`get_generator` which are then passed
            to whatever callback is used based on the ``export`` argument.

            If ``export`` is not supplied, see
            :meth:`axonius_api_client.api.asset_callbacks.base.Base.args_map`.

            If ``export`` equals ``json``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_json.Json.args_map`.

            If ``export`` equals ``csv``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_csv.Csv.args_map`.

            If ``export`` equals ``json_to_csv``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_json_to_csv.JsonToCsv.args_map`.

            If ``export`` equals ``table``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_table.Table.args_map`.

            If ``export`` equals ``xlsx``, see
            :meth:`axonius_api_client.api.asset_callbacks.base_xlsx.Xlsx.args_map`.

        Args:
            generator: return an iterator for assets that will yield rows as they are fetched
            **kwargs: passed to :meth:`get_generator`
        """
        gen = self.get_generator(**kwargs)
        return gen if generator else list(gen)

    def get_generator(
        self,
        query: Optional[str] = None,
        fields: Optional[Union[List[str], str]] = None,
        fields_manual: Optional[Union[List[str], str]] = None,
        fields_regex: Optional[Union[List[str], str]] = None,
        fields_fuzzy: Optional[Union[List[str], str]] = None,
        fields_default: bool = True,
        fields_root: Optional[str] = None,
        max_rows: Optional[int] = None,
        max_pages: Optional[int] = None,
        row_start: int = 0,
        page_size: int = MAX_PAGE_SIZE,
        page_start: int = 0,
        page_sleep: int = 0,
        use_cursor: bool = True,
        export: str = DEFAULT_CALLBACKS_CLS,
        include_details: bool = False,
        sort_field: Optional[str] = None,
        sort_descending: bool = False,
        history_date: Optional[Union[str, timedelta, datetime]] = None,
        wiz_entries: Optional[List[dict]] = None,
        **kwargs,
    ) -> Generator[dict, None, None]:
        """Get assets from a query.

        Args:
            query: if supplied, only get the assets that match the query
            fields: fields to return for each asset (will be validated)
            fields_manual: fields to return for each asset (will NOT be validated)
            fields_regex: regex of fields to return for each asset
            fields_fuzzy: string to fuzzy match of fields to return for each asset
            fields_default: include the default fields in :attr:`fields_default`
            fields_root: include all fields of an adapter that are not complex sub-fields
            max_rows: only return N rows
            max_pages: only return N pages
            row_start: start at row N
            page_size: fetch N rows per page
            page_start: start at page N
            page_sleep: sleep for N seconds between each page fetch
            use_cursor: use the endpoint that fetches rows using a DB cursor
            export: export assets using a callback method
            include_details: include details fields showing the adapter source of agg values
            sort_field: sort the returned assets on a given field
            sort_descending: reverse the sort of the returned assets
            history_date: return assets for a given historical date
            wiz_entries: wizard expressions to create query from
            **kwargs: passed thru to the asset callback defined in ``export``
        """
        query = self.wizard.parse(entries=wiz_entries)["query"] if wiz_entries else query
        page_size = self._get_page_size(page_size=page_size, max_rows=max_rows)

        fields = self.fields.validate(
            fields=fields,
            fields_manual=fields_manual,
            fields_regex=fields_regex,
            fields_default=fields_default,
            fields_root=fields_root,
            fields_fuzzy=fields_fuzzy,
        )

        if sort_field:
            sort_field = self.fields.get_field_name(value=sort_field)

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
        callbacks = callbacks_cls(apiobj=self, getargs=kwargs, state=state, store=store)
        self.LAST_CALLBACKS = callbacks

        callbacks.start()

        self.LOG.info(f"STARTING FETCH store={json_dump(store)}")
        self.LOG.debug(f"STARTING FETCH state={json_dump(state)}")

        while not state["stop_fetch"]:
            if state["use_cursor"]:
                page = self._page_cursor(state=state, store=store)
            else:
                page = self._page_normal(state=state, store=store)

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
                proc_rows = callbacks.process_row(row=row)

                for proc_row in listify(obj=proc_rows):
                    yield proc_row

                if state["stop_fetch"]:  # pragma: no cover
                    break

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

    def get_by_saved_query(
        self, name: str, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Get assets that would be returned by a saved query.

        Examples:
            First, create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
            ``apiobj`` is ``client.devices`` or ``client.users``

            >>> apiobj = client.devices

            Get assets from a saved query with complex fields flattened

            >>> assets = apiobj.get_by_saved_query(name="test", field_flatten=True)

        Notes:
            The query and the fields defined in the saved query will be used to
            get the assets.

        Args:
            name: name of saved query to get assets from
            **kwargs: passed to :meth:`get`
        """
        sq = self.saved_query.get_by_name(value=name)
        kwargs["query"] = sq["view"]["query"]["filter"]
        kwargs["fields_manual"] = sq["view"]["fields"]
        kwargs.setdefault("fields_default", False)
        return self.get(**kwargs)

    def get_by_id(self, id: str) -> dict:
        """Get the full data set of all adapters for a single asset.

        Examples:
            >>> asset = apiobj.get_by_id(id="3d69adf54879faade7a44068e4ecea6e")

        Args:
            id: internal_axon_id of asset to get all data set for

        Raises:
            :exc:`NotFoundError`: if id is not found

        """
        try:
            return self._get_by_id(id=id)
        except JsonError:
            otype = self.router.OBJ_TYPE
            msg = f"Failed to find internal_axon_id {id!r} for {otype}"
            raise NotFoundError(msg)

    @property
    def fields_default(self) -> List[dict]:
        """Fields to use by default for getting assets."""
        raise NotImplementedError  # pragma: no cover

    def destroy(self, destroy: bool, history: bool) -> dict:  # pragma: no cover
        """Delete ALL assets.

        Notes:
            Enable the ``Enable API destroy endpoints`` setting under
            ``Settings > Global Settings > API Settings > Enable advanced API settings``
            for this method to function.

        Args:
            destroy: Must be true in order to actually perform the delete
            history: Also delete all historical information
        """
        return self._destroy(destroy=destroy, history=history)

    def get_by_values(
        self,
        values: List[str],
        field: str,
        not_flag: bool = False,
        pre: str = "",
        post: str = "",
        field_manual: bool = False,
        **kwargs,
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where field in values.

        Notes:
            It is better to use :attr:`wizard`, :attr:`wizard_text`, or :attr:`wizard_csv`
            to build queries!

        Args:
            values: list of values that must match field
            field: name of field to query against
            not_flag: prefix query with 'not'
            pre: query to add to the beginning of the query
            post: query to add to the end of the query
            field_manual: consider supplied field as a fully qualified field name
            **kwargs: passed to :meth:`get`
        """
        field = self.fields.get_field_name(value=field, field_manual=field_manual)

        match = listify(values)
        match = [f"'{x.strip()}'" for x in match]
        match = ", ".join(match)

        inner = f"{field} in [{match}]"

        kwargs["query"] = self._build_query(
            inner=inner,
            pre=pre,
            post=post,
            not_flag=not_flag,
        )

        return self.get(**kwargs)

    def get_by_value_regex(
        self,
        value: str,
        field: str,
        cast_insensitive: bool = True,
        not_flag: bool = False,
        pre: str = "",
        post: str = "",
        field_manual: bool = False,
        **kwargs,
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where field regex matches a value.

        Notes:
            It is better to use :attr:`wizard`, :attr:`wizard_text`, or :attr:`wizard_csv`
            to build queries!

        Args:
            value: regex that must match field
            field: name of field to query against
            case_insensitive: ignore case when performing the regex match
            not_flag: prefix query with 'not'
            pre: query to add to the beginning of the query
            post: query to add to the end of the query
            field_manual: consider supplied field as a fully qualified field name
            **kwargs: passed to :meth:`get`
        """
        field = self.fields.get_field_name(value=field, field_manual=field_manual)
        flags = ', "i"' if cast_insensitive else ""
        inner = f'{field} == regex("{value}"{flags})'
        kwargs["query"] = self._build_query(
            inner=inner,
            pre=pre,
            post=post,
            not_flag=not_flag,
        )
        return self.get(**kwargs)

    def get_by_value(
        self,
        value: str,
        field: str,
        not_flag: bool = False,
        pre: str = "",
        post: str = "",
        field_manual: bool = False,
        **kwargs,
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Build a query to get assets where field equals a value.

        Notes:
            It is better to use :attr:`wizard`, :attr:`wizard_text`, or :attr:`wizard_csv`
            to build queries!

        Args:
            value: value that must equal field
            field: name of field to query against
            not_flag: prefix query with 'not'
            pre: query to add to the beginning of the query
            post: query to add to the end of the query
            field_manual: consider supplied field as a fully qualified field name
            **kwargs: passed to :meth:`get`
        """
        field = self.fields.get_field_name(value=field, field_manual=field_manual)

        inner = f'{field} == "{value}"'

        kwargs["query"] = self._build_query(
            inner=inner,
            pre=pre,
            post=post,
            not_flag=not_flag,
        )

        return self.get(**kwargs)

    def history_dates(self) -> dict:
        """Get all known historical dates."""
        return self._history_dates()

    def validate_history_date(self, value: Union[str, timedelta, datetime]) -> str:
        """Validate that a given date is known historical date.

        Args:
            value: date time to validate

        Raises:
            :exc:`ApiError`: if supplied value is not an available history date to pick from
        """
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
        """Query builder with basic functionality.

        Notes:
            It is better to use :attr:`wizard`, :attr:`wizard_text`, or :attr:`wizard_csv`
            to build queries!

        Args:
            inner: inner query portion to wrap in parens and prefix with not
            not_flag: prefix query with 'not'
            pre: query to add to the beginning of the query
            post: query to add to the end of the query
        """
        if not_flag:
            inner = f"(not ({inner}))"
        else:
            inner = f"({inner})"

        lines = [pre, inner, post]
        query = " ".join([x.strip() for x in lines if x.strip()]).strip()

        self.LOG.debug(f"Built query: {query!r}")
        return query

    def _init(self, **kwargs):
        """Post init method for subclasses to use for extra setup."""
        from ..adapters import Adapters
        from ..asset_callbacks import Base
        from .fields import Fields
        from .labels import Labels
        from .saved_query import SavedQuery

        self.adapters: Adapters = Adapters(auth=self.auth, **kwargs)
        """Adapters API model for cross reference."""

        self.labels: Labels = Labels(parent=self)
        """Work with labels (tags)."""

        self.saved_query: SavedQuery = SavedQuery(parent=self)
        """Work with saved queries."""

        self.fields: Fields = Fields(parent=self)
        """Work with fields."""

        self.wizard: Wizard = Wizard(apiobj=self)
        """Query wizard builder."""

        self.wizard_text: WizardText = WizardText(apiobj=self)
        """Query wizard builder from text."""

        self.wizard_csv: WizardCsv = WizardCsv(apiobj=self)
        """Query wizard builder from CSV."""

        self.LAST_GET: dict = {}
        """Request object sent for last :meth:`get` request"""

        self.LAST_CALLBACKS: Base = None
        """Callbacks object used for last :meth:`get` request."""

        super(AssetMixin, self)._init(**kwargs)

    def _page_cursor(self, state: dict, store: dict) -> dict:
        """Get a page of assets using the cursor get method.

        Args:
            state: current state tracker of :meth:`get`
            store: current store tracker of :meth:`get`
        """
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
        state["rows_to_fetch_left"] = state["rows_to_fetch_total"] - state["rows_fetched_total"]
        state["pages_to_fetch_total"] = math.ceil(state["rows_to_fetch_total"] / state["page_size"])
        state["pages_to_fetch_left"] = math.ceil(state["rows_to_fetch_left"] / state["page_size"])

        state["page_cursor"] = page.get("cursor")
        return page

    def _page_normal(self, state: dict, store: dict) -> dict:
        """Get a page of assets using the normal get method.

        Args:
            state: current state tracker of :meth:`get`
            store: current store tracker of :meth:`get`
        """
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
        state["rows_to_fetch_left"] = state["rows_to_fetch_total"] - state["rows_fetched_total"]
        state["page_number"] = page["page"]["number"]
        state["pages_to_fetch_total"] = page["page"]["totalPages"]
        state["pages_to_fetch_left"] = state["pages_to_fetch_total"] - state["page_number"]
        return page

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
        """Private API method to get a page of assets.

        Args:
            query: if supplied, only return the assets that match the query
            fields: CSV or list of fields to include in return
            row_start: start at row N
            page_size: fetch N assets
            include_details: include details fields showing the adapter source of agg values
            sort_field: sort the returned assets on a given field
            sort_descending: reverse the sort of the returned assets
            history_date: return assets for a given historical date
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

        self.LAST_GET: dict = params

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
        """Private API method to get a page of assets using a cursor.

        Args:
            query: if supplied, only return the assets that match the query
            fields: CSV or list of fields to include in return
            row_start: start at row N
            page_size: fetch N assets
            include_details: include details fields showing the adapter source of agg values
            sort_field: sort the returned assets on a given field
            sort_descending: reverse the sort of the returned assets
            history_date: return assets for a given historical date
            cursor: cursor returned by previous call to continue paging through
        """
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

        self.LAST_GET: dict = params
        return self.request(method="post", path=self.router.cached, json=params)

    def _get_by_id(self, id: str) -> dict:
        """Private API method to get the full metadata of all adapters for a single asset.

        Args:
            id: internal_axon_id of asset to get all metadata for
        """
        path = self.router.by_id.format(id=id)
        return self.request(method="get", path=path)

    def _count(
        self,
        query: Optional[str] = None,
        history_date: Optional[str] = None,
    ) -> int:
        """Private API method to get the count of assets.

        Args:
            query: if supplied, only return the count of assets that match the query
            history_date: return count for a given historical date
        """
        params = {}
        params["filter"] = query
        params["history"] = history_date
        return self.request(method="post", path=self.router.count, json=params)

    def _destroy(self, destroy: bool, history: bool) -> dict:  # pragma: no cover
        """Private API method to destroy ALL assets.

        Args:
            destroy: Must be true in order to actually perform the delete
            history: Also delete all historical information
        """
        data = {"destroy": destroy, "history": history}
        path = self.router.destroy
        return self.request(method="post", path=path, json=data)

    def _history_dates(self) -> dict:
        """Private API method to get all known historical dates."""
        path = self.router.history_dates
        return self.request(method="get", path=path)

    FIELD_TAGS: str = "labels"
    """Field name for getting tabs (labels)."""

    FIELD_AXON_ID: str = "internal_axon_id"
    """Field name for asset unique ID."""

    FIELD_ADAPTERS: str = "adapters"
    """Field name for list of adapters on an asset."""

    FIELD_ADAPTER_LEN: str = "adapter_list_length"
    """Field name for count of adapters on an asset."""

    FIELD_LAST_SEEN: str = "specific_data.data.last_seen"
    """Field name for last time an adapter saw the asset."""

    FIELD_MAIN: str = FIELD_AXON_ID
    """Field name of the main identifier."""

    FIELD_SIMPLE: str = FIELD_AXON_ID
    """Field name of a simple field."""

    FIELD_COMPLEX: str = None
    """Field name of a complex field."""

    FIELD_COMPLEX_SUB: str = None
    """Field name of a complex sub field."""

    FIELDS_API: List[str] = [
        FIELD_AXON_ID,
        FIELD_ADAPTERS,
        FIELD_TAGS,
        FIELD_ADAPTER_LEN,
    ]
    """Field names that are always returned by the REST API no matter what fields are selected"""

    wizard: str = None
    """:obj:`axonius_api_client.api.wizards.wizard.Wizard`: Query wizard for python objects."""

    wizard_text: str = None
    """:obj:`axonius_api_client.api.wizards.wizard_text.WizardText`: Query wizard for text files."""

    wizard_csv = None
    """:obj:`axonius_api_client.api.wizards.wizard_csv.WizardCsv`: Query wizard for CSV files."""
