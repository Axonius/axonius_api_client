# -*- coding: utf-8 -*-
"""API for working with saved queries for assets."""
from typing import Generator, List, Optional, Union

from ...constants.api import MAX_PAGE_SIZE
from ...exceptions import NotFoundError
from ...parsers.tables import tablize_sqs
from ...tools import check_gui_page_size, listify
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ChildMixins


# XXX need update saved query
class SavedQuery(ChildMixins):
    """API object for working with saved queries for the parent asset type.

    Examples:
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
        ``apiobj`` is either ``client.devices`` or ``client.users``

        >>> apiobj = client.devices  # or client.users

        * Get a saved query by name: :meth:`get_by_name`
        * Get a saved query by UUID: :meth:`get_by_uuid`
        * Get a saved query by tags: :meth:`get_by_tags`
        * Get all saved query tags: :meth:`get_tags`
        * Get all saved queries: :meth:`get`
        * Add a saved query: :meth:`add`
        * Delete a saved query by name: :meth:`delete_by_name`
        * Delete a saved query by UUID or SQ object: :meth:`delete`

    See Also:
        * Device assets :obj:`axonius_api_client.api.assets.devices.Devices`
        * User assets :obj:`axonius_api_client.api.assets.users.Users`

    """

    def get_by_name(self, value: str) -> dict:
        """Get a saved query by name.

        Examples:
            Get a saved query by name

            >>> sq = apiobj.saved_query.get_by_name(name="test")
            >>> sq['tags']
            ['Unmanaged Devices']
            >>> sq['description'][:80]
            'Devices that have been seen by at least one agent or at least one endpoint manag'
            >>> sq['view']['fields']
            [
                'adapters',
                'specific_data.data.name',
                'specific_data.data.hostname',
                'specific_data.data.last_seen',
                'specific_data.data.network_interfaces.manufacturer',
                'specific_data.data.network_interfaces.mac',
                'specific_data.data.network_interfaces.ips',
                'specific_data.data.os.type',
                'labels'
            ]
            >>> sq['view']['query']['filter'][:80]
            '(specific_data.data.adapter_properties == "Agent") or (specific_data.data.adapte'

        Args:
            value: name of saved query
        """
        data = self.get()
        found = [x for x in data if x["name"] == value]
        if found:
            return found[0]

        err = f"Saved Query with name of {value!r} not found"
        raise NotFoundError(tablize_sqs(data=data, err=err))

    def get_by_uuid(self, value: str) -> dict:
        """Get a saved query by uuid.

        Examples:
            Get a saved query by uuid

            >>> sq = apiobj.saved_query.get_by_uuid(value="5f76721ce4557d5cba93f59e")

        Args:
            value: uuid of saved query
        """
        data = self.get()
        found = [x for x in data if x["uuid"] == value]
        if found:
            return found[0]

        err = f"Saved Query with UUID of {value!r} not found"
        raise NotFoundError(tablize_sqs(data=data, err=err))

    def get_by_tags(self, value: Union[str, List[str]], **kwargs) -> List[dict]:
        """Get saved queries by tags.

        Examples:
            Get all saved queries with tagged with 'AD'

            >>> sqs = apiobj.saved_query.get_by_tags('AD')
            >>> len(sqs)
            2

            Get all saved queries with tagged with 'AD' or 'AWS'

            >>> sqs = apiobj.saved_query.get_by_tags(['AD', 'AWS'])
            >>> len(sqs)
            5

        Args:
            value: list of tags
            **kwargs: passed to :meth:`get`

        Raises:
            :exc:`NotFoundError`: if no saved queries found tagged with supplied tags
        """
        value = listify(value)
        rows = self.get(**kwargs)
        matches = []
        known = set()

        for row in rows:
            for tag in row.get("tags", []):
                known.add(tag)
                if tag in value and row not in matches:
                    matches.append(row)

        if not matches:
            valid = "\n  " + "\n  ".join(sorted(list(known)))
            msg = f"No saved query found with tags {value!r}, valid tags:{valid}"
            raise NotFoundError(msg)
        return matches

    def get_tags(self, **kwargs) -> List[str]:
        """Get all tags for saved queries.

        Examples:
            Get all known tags for all saved queries

            >>> tags = apiobj.saved_query.get_tags()
            >>> len(tags)
            19

        Args:
            **kwargs: passed to :meth:`get`
        """
        rows = self.get(**kwargs)
        tags = [y for x in rows for y in x.get("tags", [])]
        return sorted(list(set(tags)))

    def get(self, generator: bool = False) -> Union[Generator[dict, None, None], List[dict]]:
        """Get all saved queries.

        Examples:
            Get all saved queries

            >>> sqs = apiobj.saved_query.get()
            >>> len(sqs)
            39

        Args:
            generator: return an iterator
        """
        gen = self.get_generator()
        return gen if generator else list(gen)

    def get_generator(self) -> Generator[dict, None, None]:
        """Get Saved Queries using a generator."""
        offset = 0

        while True:
            rows = self._get(offset=offset)
            offset += len(rows)

            if not rows:
                break

            for row in rows:
                yield row.to_dict()

    def add(
        self,
        name: str,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        expressions: Optional[List[str]] = None,
        fields: Optional[Union[List[str], str]] = None,
        fields_manual: Optional[Union[List[str], str]] = None,
        fields_regex: Optional[Union[List[str], str]] = None,
        fields_fuzzy: Optional[Union[List[str], str]] = None,
        fields_default: bool = True,
        fields_root: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_descending: bool = True,
        column_filters: Optional[dict] = None,
        gui_page_size: Optional[int] = None,
        private: bool = False,
        always_cached: bool = False,
        **kwargs,
    ) -> dict:
        """Create a saved query.

        Examples:
            Create a saved query using a :obj:`axonius_api_client.api.wizards.wizard.Wizard`

            >>> parsed = apiobj.wizard_text.parse(content="simple hostname contains blah")
            >>> query = parsed["query"]
            >>> expressions = parsed["expressions"]
            >>> sq = apiobj.saved_query.add(
            ...     name="test",
            ...     query=query,
            ...     expressions=expressions,
            ...     description="meep meep",
            ...     tags=["nyuck1", "nyuck2", "nyuck3"],
            ... )

        Notes:
            Saved Queries created without expressions will not be editable using the query wizard
            in the GUI. Use :obj:`axonius_api_client.api.wizards.wizard.Wizard` to produce a query
            and it's accordant expressions for the GUI query wizard.

        Args:
            name: name of saved query
            description: description
            tags: list of tags
            expressions: expressions built by :obj:`axonius_api_client.api.wizards.wizard.Wizard`
            query: query built by GUI or the CLI query wizard
            fields: fields to return for each asset (will be validated)
            fields_manual: fields to return for each asset (will NOT be validated)
            fields_regex: regex of fields to return for each asset
            fields_fuzzy: string to fuzzy match of fields to return for each asset
            fields_default: include the default fields defined in the parent asset object
            fields_root: include all fields of an adapter that are not complex sub-fields
            sort_field: sort the returned assets on a given field
            sort_descending: reverse the sort of the returned assets
            column_filters: column filters keyed as field_name:value
            gui_page_size: show N rows per page in GUI
            private: make this saved query private to current user
        """
        query_expr: Optional[str] = kwargs.get("query_expr", None) or query
        gui_page_size = check_gui_page_size(size=gui_page_size)

        fields = self.parent.fields.validate(
            fields=fields,
            fields_manual=fields_manual,
            fields_regex=fields_regex,
            fields_default=fields_default,
            fields_root=fields_root,
            fields_fuzzy=fields_fuzzy,
        )

        if sort_field:
            sort_field = self.parent.fields.get_field_name(value=sort_field)

        data_column_filters = {}
        if column_filters:
            for col_field, col_value in column_filters.items():
                col_field = self.parent.fields.get_field_name(value=col_field)
                data_column_filters[col_field] = col_value

        dmeta = {}  # TBD
        dmeta["enforcementFilter"] = None  # TBD
        dmeta["uniqueAdapters"] = False  # TBD

        data_query = {}
        data_query["filter"] = query or ""
        if query_expr:
            data_query["onlyExpressionsFilter"] = query_expr
        data_query["expressions"] = expressions or []
        data_query["search"] = None  # TBD
        data_query["meta"] = dmeta  # TBD

        data_sort = {}
        data_sort["desc"] = sort_descending
        data_sort["field"] = sort_field or ""

        data_view = {}
        data_view["query"] = data_query
        data_view["sort"] = data_sort
        data_view["fields"] = fields
        data_view["pageSize"] = gui_page_size
        data_view["colFilters"] = data_column_filters or {}
        data_view["colExcludedAdapters"] = {}  # TBD

        # data = {}
        # data["name"] = name
        # data["query_type"] = "saved"
        # data["description"] = description
        # data["view"] = data_view
        # data["tags"] = tags or []
        # data["private"] = private

        added = self._add(
            name=name,
            description=description,
            view=data_view,
            private=private,
            always_cached=always_cached,
            tags=tags,
        )
        return self.get_by_uuid(value=added.id)

    def delete_by_name(self, value: str, **kwargs) -> dict:
        """Delete a saved query by name.

        Examples:
            Delete the saved query by name

            >>> deleted = apiobj.saved_query.delete_by_name(name="test")

        Args:
            value: name of saved query to delete
            **kwargs: passed to :meth:`get_by_name`
        """
        row = self.get_by_name(value=value, **kwargs)
        self._delete(uuid=row["uuid"])
        return row

    def delete(self, rows: Union[str, List[str], List[dict]]) -> List[str]:
        """Delete saved queries.

        Args:
            rows: list of UUIDs or rows previously fetched saved queries to delete
        """
        rows = listify(rows)
        deleted = []
        for row in rows:
            uuid = row["uuid"] if isinstance(row, dict) else row
            self._delete(uuid=uuid)
            deleted.append(uuid)
        return deleted

    def _add(
        self,
        name: str,
        view: dict,
        description: Optional[str] = "",
        always_cached: bool = False,
        private: bool = False,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Direct API method to create a saved query.

        Args:
            data: saved query metadata
        """
        api_endpoint = ApiEndpoints.saved_queries.create
        request_obj = api_endpoint.load_request(
            name=name,
            view=view,
            description=description,
            always_cached=always_cached,
            private=private,
            tags=tags or [],
        )
        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=self.parent.ASSET_TYPE
        )

    def _delete(self, uuid: str) -> json_api.generic.Metadata:
        """Direct API method to delete saved queries.

        Args:
            ids: list of uuid's to delete
        """
        api_endpoint = ApiEndpoints.saved_queries.delete
        request_obj = api_endpoint.load_request()
        return api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            asset_type=self.parent.ASSET_TYPE,
            uuid=uuid,
        )

    def _get(
        self, limit: int = MAX_PAGE_SIZE, offset: int = 0
    ) -> List[json_api.saved_queries.SavedQuery]:
        """Direct API method to get all users.

        Args:
            limit: limit to N rows per page
            offset: start at row N
        """
        api_endpoint = ApiEndpoints.saved_queries.get
        request_obj = api_endpoint.load_request(page={"limit": limit, "offset": offset})
        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=self.parent.ASSET_TYPE
        )
