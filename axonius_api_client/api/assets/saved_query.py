# -*- coding: utf-8 -*-
"""API for working with saved queries for assets."""
from typing import Generator, List, Optional, Union

from ...constants.api import PAGE_SIZE
from ...exceptions import NotFoundError
from ...tools import check_gui_page_size, listify
from ..mixins import ChildMixins, PagingMixinsObject


# XXX need update saved query
class SavedQuery(ChildMixins, PagingMixinsObject):
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

    def get_by_name(self, value: str, **kwargs) -> dict:
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
            **kwargs: passed to :meth:`get`
        """
        return super().get_by_name(value=value, **kwargs)

    def get_by_uuid(self, value: str, **kwargs) -> dict:
        """Get a saved query by uuid.

        Examples:
            Get a saved query by uuid

            >>> sq = apiobj.saved_query.get_by_uuid(uuid="5f76721ce4557d5cba93f59e")

        Args:
            value: uuid of saved query
            **kwargs: passed to :meth:`get`
        """
        return super().get_by_uuid(value=value, **kwargs)

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

    def get(
        self, generator: bool = False, **kwargs
    ) -> Union[Generator[dict, None, None], List[dict]]:
        """Get all saved queries.

        Examples:
            Get all saved queries

            >>> sqs = apiobj.saved_query.get()
            >>> len(sqs)
            39

        Args:
            generator: return an iterator
            **kwargs: passed to :meth:`get_generator`
        """
        return super().get(generator=generator, **kwargs)

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

        data = {}
        data["name"] = name
        data["query_type"] = "saved"
        data["description"] = description
        data["view"] = data_view
        data["tags"] = tags or []
        data["private"] = private

        added = self._add(data=data)
        return self.get_by_uuid(value=added)

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
        self.delete(rows=[row])
        return row

    def delete(self, rows: Union[str, List[dict]]) -> List[dict]:
        """Delete saved queries.

        Args:
            rows: list of UUIDs or rows previously fetched saved queries to delete
        """
        rows = listify(rows)
        ids = [x["uuid"] if isinstance(x, dict) else x for x in rows]
        self._delete(ids=list(set(ids)))
        return rows

    def _add(self, data: dict) -> str:
        """Direct API method to create a saved query.

        Args:
            data: saved query metadata
        """
        path = self.router.views
        return self.request(method="put", path=path, json=data)

    def _delete(self, ids: List[str]) -> str:
        """Direct API method to delete saved queries.

        Args:
            ids: list of uuid's to delete
        """
        data = {"ids": listify(ids)}
        path = f"{self.router.views}/saved"
        return self.request(method="delete", path=path, json=data)

    def _get(
        self, query: Optional[str] = None, row_start: int = 0, page_size: int = PAGE_SIZE
    ) -> List[dict]:
        """Direct API method to get saved queries.

        Args:
            query: filter rows to return
            row_start: start at row N
            page_size: fetch N assets
        """
        params = {}
        params["limit"] = page_size
        params["skip"] = row_start
        params["filter"] = query
        path = f"{self.router.views}/saved"
        return self.request(method="get", path=path, params=params)
