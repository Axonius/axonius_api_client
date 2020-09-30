# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from typing import List, Optional, Union

from ...constants import GUI_PAGE_SIZES, PAGE_SIZE
from ...exceptions import ApiError, NotFoundError
from ...tools import listify
from ..mixins import ChildMixins, PagingMixinsObject


def check_gui_page_size(size: Optional[int] = None) -> int:
    """Check page size to see if it one of the valid GUI page sizes.

    Args:
        size: page size to check

    Raises:
        :exc:`ApiError`: if size is not one of :data:`axonius_api_client.constants.GUI_PAGE_SIZES`
    """
    size = size or GUI_PAGE_SIZES[0]
    if size not in GUI_PAGE_SIZES:
        raise ApiError(f"gui_page_size of {size} is invalid, must be one of {GUI_PAGE_SIZES}")
    return size


class SavedQuery(ChildMixins, PagingMixinsObject):
    """API object for working with saved queries for the parent asset type.

    Examples:
        First, create a ``client`` using :obj:`axonius_api_client.connect.Connect`.

        >>> # Get a saved query
        >>> sq = client.devices.saved_query.get(name="test")
        >>>
        >>> # See the fields defined in the saved query
        >>> print(sq['view']['fields'])
        >>>
        >>> # See the query defined in the saved query
        >>> print(sq['view']['query']['filter'])
        >>>
        >>> # Delete the saved query
        >>> deleted = client.devices.saved_query.delete(rows=[sq])
        >>>
        >>> # Delete the saved query by name
        >>> deleted = client.devices.saved_query.delete_by_name(name="test")

        Create a saved query using a :obj:`axonius_api_client.api.wizard.wizard.Wizard`

        >>> parsed = client.devices.wizard_text.parse(content="simple hostname contains blah")
        >>> query = parsed["query"]
        >>> expressions = parsed["expressions"]
        >>> sq = devices.saved_query.add(
        ...     name="test",
        ...     query=query,
        ...     expressions=expressions,
        ...     description="meep meep",
        ...     tags=["nyuck1", "nyuck2", "nyuck3"],
        ... )

    """

    # XXX need update saved query, doc the other methods (get tags, get_by_tags, etc)

    def get_by_tags(self, value: Union[str, List[str]], **kwargs) -> List[dict]:
        """Get saved queries by tags.

        Args:
            value: list of tags
            **kwargs: passed to :meth:`get`
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

        Args:
            **kwargs: passed to :meth:`get`
        """
        rows = self.get(**kwargs)
        tags = [y for x in rows for y in x.get("tags", [])]
        return sorted(list(set(tags)))

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

        Notes:
            Saved Queries created without expressions will not be editable using the query wizard
            in the GUI. Use :obj:`axonius_api_client.api.wizard.wizard.Wizard` to produce a query
            and it's accordant expressions for the GUI query wizard.

        Args:
            name: name of saved query
            description: description
            tags: list of tags
            expressions: expressions built by :obj:`axonius_api_client.api.wizard.wizard.Wizard`
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

    def delete(self, rows: List[dict]) -> List[dict]:
        """Delete saved queries.

        Args:
            rows: previously fetched saved queries to delete
        """
        rows = listify(rows)
        ids = [x["uuid"] for x in rows]
        self._delete(ids=list(set(ids)))
        return rows

    def delete_by_name(self, value: str, **kwargs) -> dict:
        """Delete a saved query by name.

        Args:
            value: name of saved query to delete
            **kwargs: passed to :meth:`get_by_name`
        """
        row = self.get_by_name(value=value, **kwargs)
        self.delete(rows=[row])
        return row

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
