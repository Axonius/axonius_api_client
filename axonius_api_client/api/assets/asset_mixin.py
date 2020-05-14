# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
import math
import time

from ...constants import MAX_PAGE_SIZE, PAGE_SIZE
from ...exceptions import JsonError, NotFoundError
from ...tools import dt_now, dt_sec_ago, json_dump, listify
from ..adapters import Adapters
from ..asset_callbacks import get_callbacks_cls
from ..mixins import ModelMixins
from .fields import Fields
from .labels import Labels
from .saved_query import SavedQuery


class AssetMixin(ModelMixins):
    """API model for working with user and device assets."""

    FIELD_TAGS = "labels"
    FIELD_AXON_ID = "internal_axon_id"
    FIELD_ADAPTERS = "adapters"
    FIELD_ADAPTER_LEN = "adapter_list_length"

    FIELDS_API = [FIELD_AXON_ID, FIELD_ADAPTERS, FIELD_TAGS, FIELD_ADAPTER_LEN]

    @property
    def fields_default(self):
        """Fields to add to all get calls for this asset type.

        Returns:
            :obj:`list` of :obj:`dict`: fields to add to
        """
        raise NotImplementedError  # pragma: no cover

    def destroy(self, destroy, history):
        """Destroy ALL assets."""
        return self._destroy(destroy=destroy, history=history)

    def count(self, query=None):
        """Get the count of assets.

        Args:
            query (:obj:`str`, optional): default ``None`` -

                * if ``None`` return the count of all assets
                * if :obj:`str` return the count of assets that match a
                  query built by the GUI query wizard

        Returns:
            :obj:`int`: count of assets matching query
        """
        return self._count(query=query)

    def count_by_saved_query(self, name):
        """Get the count of assets that would be returned by a saved query.

        Args:
            name (:obj:`str`): name of saved query to get count of assets from

        Returns:
            :obj:`int`: count of assets matching query in saved query
        """
        sq = self.saved_query.get_by_name(value=name)
        return self._count(query=sq["view"]["query"]["filter"])

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
        fields=None,
        fields_manual=None,
        fields_regex=None,
        fields_default=True,
        fields_map=None,
        max_rows=None,
        max_pages=None,
        page_size=MAX_PAGE_SIZE,
        page_start=0,
        page_sleep=0,
        use_cursor=True,
        export=None,
        **kwargs,
    ):
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
        page_size = self._get_page_size(page_size=page_size, max_rows=None)

        fields_map = fields_map or self.fields.get()

        fields = self.fields.validate(
            fields=fields,
            fields_manual=fields_manual,
            fields_regex=fields_regex,
            fields_default=fields_default,
            fields_map=fields_map,
        )

        store = {
            "query": query,
            "fields": fields,
        }

        state = {
            "max_pages": max_pages,
            "max_rows": max_rows,
            "use_cursor": use_cursor,
            "page_cursor": None,
            "page_sleep": page_sleep,
            "page_size": page_size,
            "page_number": 1,
            "pages_to_fetch_left": None,
            "pages_to_fetch_total": None,
            "rows_to_fetch_left": None,
            "rows_to_fetch_total": None,
            "rows_fetched_this_page": None,
            "rows_fetched_total": 0,
            "rows_processed_total": 0,
            "fetch_seconds_total": 0,
            "fetch_seconds_this_page": None,
            "stop_fetch": False,
            "stop_msg": None,
        }

        if not use_cursor:
            state["page_number"] = page_start or 1
            state["page_start"] = page_start

            if page_start > 1:
                state["rows_fetched_total"] = page_start * page_size

        callbacks_cls = get_callbacks_cls(export=export)

        self._LAST_CALLBACKS = callbacks = callbacks_cls(
            apiobj=self,
            fields_map=fields_map,
            getargs=kwargs,
            fields=fields,
            query=query,
            state=state,
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
                row_items = callbacks.row(row=row)

                for row_item in listify(obj=row_items):
                    yield row_item

                state["rows_processed_total"] += 1

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

        callbacks.stop()

        self.LOG.info(f"FINISHED FETCH store={store}")
        self.LOG.debug(f"FINISHED FETCH state={json_dump(state)}")

    def _get_page_cursor(self, state, store):
        page_start_dt = dt_now()

        page = self._get_cursor(
            query=store["query"],
            fields=store["fields"],
            page_size=state["page_size"],
            cursor=state["page_cursor"],
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

    def _get_page_normal(self, state, store):
        page_start_dt = dt_now()

        page = self._get(
            query=store["query"],
            fields=store["fields"],
            row_start=state["rows_fetched_total"],
            page_size=state["page_size"],
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

    def get_by_id(self, id):
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

    def get_by_saved_query(self, name, **kwargs):
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
        values,
        field,
        not_flag=False,
        pre="",
        post="",
        field_manual=False,
        fields_map=None,
        **kwargs,
    ):
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
        value,
        field,
        cast_insensitive=True,
        not_flag=False,
        pre="",
        post="",
        field_manual=False,
        fields_map=False,
        **kwargs,
    ):
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
        value,
        field,
        not_flag=False,
        pre="",
        post="",
        field_manual=False,
        fields_map=False,
        **kwargs,
    ):
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

    def _build_query(self, inner, not_flag=False, pre="", post=""):
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

    def _init(self, auth, **kwargs):
        """Post init method for subclasses to use for extra setup.

        Args:
            auth (:obj:`.auth.Model`): object to use for auth and sending API requests
        """
        # cross reference
        self.adapters = Adapters(auth=auth, **kwargs)

        # children
        self.labels = Labels(parent=self)
        self.saved_query = SavedQuery(parent=self)
        self.fields = Fields(parent=self)

        super(AssetMixin, self)._init(auth=auth, **kwargs)

    def _count(self, query=None):
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
        if query:
            params["filter"] = query

        return self.request(method="post", path=self.router.count, json=params)

    def _get(self, query=None, fields=None, row_start=0, page_size=PAGE_SIZE):
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

        if query:
            params["filter"] = query

        if fields:
            if isinstance(fields, list):
                fields = ",".join(fields)

            params["fields"] = fields

        self._LAST_GET = params

        return self.request(method="post", path=self.router.root, json=params)

    def _get_cursor(self, query=None, fields=None, page_size=PAGE_SIZE, cursor=None):
        """Get a page for a given query."""
        page_size = self._get_page_size(page_size=page_size, max_rows=None)

        params = {}
        params["cursor"] = cursor
        params["limit"] = page_size

        if query:
            params["filter"] = query

        if fields:
            if isinstance(fields, list):
                fields = ",".join(fields)

            params["fields"] = fields

        self._LAST_GET = params

        return self.request(method="post", path=self.router.cached, json=params)

    def _get_by_id(self, id):
        """Direct API method to get the full metadata of all adapters for a single asset.

        Args:
            id (:obj:`str`): internal_axon_id of asset to get all metadata for

        Returns:
            :obj:`dict`: dict with all metadata for all adapters for asset with
                **id** of internal_axon_id
        """
        path = self.router.by_id.format(id=id)
        return self.request(method="get", path=path)

    def _destroy(self, destroy, history):
        """Destroy ALL assets."""
        data = {"destroy": destroy, "history": history}
        path = self.router.destroy
        return self.request(method="post", path=path, json=data)
