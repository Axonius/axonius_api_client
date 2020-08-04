# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from typing import List, Optional, Union

from ...constants import GUI_PAGE_SIZES, PAGE_SIZE
from ...exceptions import ApiError, NotFoundError
from ...tools import listify
from ..mixins import ChildMixins, PagingMixinsObject


def check_gui_page_size(size: Optional[int] = None) -> int:
    """Pass."""
    if size:
        if size not in GUI_PAGE_SIZES:
            raise ApiError(
                f"gui_page_size of {size} is invalid, must be one of {GUI_PAGE_SIZES}"
            )
    else:
        size = GUI_PAGE_SIZES[0]
    return size


class SavedQuery(ChildMixins, PagingMixinsObject):
    """ChildMixins API model for working with saved queries for the parent asset type."""

    def get_by_tags(self, value: Union[str, List[str]], **kwargs) -> List[dict]:
        """Get saved queries by tags."""
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
        """Get all tags for saved queries."""
        rows = self.get(**kwargs)
        tags = [y for x in rows for y in x.get("tags", [])]
        return sorted(list(set(tags)))

    def add(
        self,
        name: str,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        fields: Optional[Union[List[str], str]] = None,
        fields_regex: Optional[Union[List[str], str]] = None,
        fields_manual: Optional[Union[List[str], str]] = None,
        fields_default: bool = True,
        sort_field: Optional[str] = None,
        sort_descending: bool = True,
        column_filters: Optional[dict] = None,
        gui_page_size: Optional[int] = None,
        fields_map: Optional[dict] = None,
        **kwargs,
    ):
        """Create a saved query.

        Warning:
            Queries created with this method will NOT show the filters in the
            query wizard!

        Args:
            name (:obj:`str`): name of saved query to create
            query (:obj:`str`): query built by GUI query wizard
            fields (:obj:`object`): fields/columns
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
            sort (:obj:`str`, optional): default ``None`` - field to sort results on
            sort_descending (:obj:`bool`, optional): default ``True`` - sort on
                **field** in descending order
            column_filters (:obj:`dict`, optional): default ``None`` - column
                filters keyed as field_name:value
            gui_page_size (:obj:`int`, optional): default ``None`` -
                show N rows per page in GUI

        Returns:
            :obj:`dict`: metadata of saved query that was created
        """
        gui_page_size = check_gui_page_size(size=gui_page_size)
        fields_map = fields_map or self.parent.fields.get()

        fields = self.parent.fields.validate(
            fields=fields,
            fields_manual=fields_manual,
            fields_regex=fields_regex,
            fields_default=fields_default,
            fields_map=fields_map,
        )

        if sort_field:
            sort_field = self.parent.fields.get_field_name(
                value=sort_field, fields_map=fields_map
            )

        data_column_filters = {}
        if column_filters:
            for col_field, col_value in column_filters.items():
                col_field = self.parent.fields.get_field_name(
                    value=col_field, fields_map=fields_map
                )
                data_column_filters[col_field] = col_value

        data_query = {}
        data_query["filter"] = query
        data_query["expressions"] = []  # query wizard generated only
        # data_query["search"] = ""  # tbd

        data_sort = {}
        data_sort["desc"] = sort_descending
        data_sort["field"] = sort_field or ""

        data_view = {}
        data_view["query"] = data_query
        data_view["sort"] = data_sort
        data_view["fields"] = fields
        data_view["pageSize"] = gui_page_size
        data_view["colFilters"] = data_column_filters or {}

        data = {}
        data["name"] = name
        data["query_type"] = "saved"
        data["description"] = description
        data["view"] = data_view
        data["tags"] = tags or []

        added = self._add(data=data)
        kwargs["value"] = added
        return self.get_by_uuid(**kwargs)

    def delete(self, rows: List[dict]) -> List[dict]:
        """Delete saved queries returned from get.

        Args:
            rows (:obj:`list` of :obj:`dict`): metadata of saved queries to delete

        Returns:
            :obj:`list` of :obj:`dict`: saved queries deleted
        """
        rows = listify(rows)
        ids = [x["uuid"] for x in rows]
        self._delete(ids=list(set(ids)))
        return rows

    def delete_by_name(self, value: str, **kwargs) -> dict:
        """Delete saved queries returned from get.

        Args:
            rows (:obj:`list` of :obj:`dict`): metadata of saved queries to delete

        Returns:
            :obj:`list` of :obj:`dict`: saved queries deleted
        """
        row = self.get_by_name(value=value, **kwargs)
        self.delete(rows=[row])
        return row

    def _add(self, data: dict) -> str:
        """Direct API method to create a saved query.

        Warning:
            Queries created with this method will NOT show the filters in the
            query wizard!

        Returns:
            :obj:`str`: ID of the saved query that was created
        """
        path = self.router.views
        return self.request(method="post", path=path, json=data)

    def _delete(self, ids: List[str]) -> str:
        """Direct API method to delete saved queries.

        Args:
            ids (:obj:`list` of :obj:`str`): list of saved query uuid's to delete

        Returns:
            :obj:`str`: empty string
        """
        data = {"ids": listify(ids)}
        path = self.router.views
        return self.request(method="delete", path=path, json=data)

    def _get(
        self, query: Optional[str] = None, row_start: int = 0, page_size: int = PAGE_SIZE
    ) -> List[dict]:
        """Direct API method to get saved queries.

        Args:
            query (:obj:`str`, optional): default ``None`` - filter rows to return

                This is NOT a query built by the query wizard!
            row_start (:obj:`int`, optional): default ``0`` - for paging, skip N rows
            page_size (:obj:`int`, optional): default ``0`` - for paging, return N rows

        Returns:
            :obj:`list` of :obj:`dict`: list of saved query metadata
        """
        params = {}
        params["limit"] = page_size
        params["skip"] = row_start
        params["filter"] = query
        path = self.router.views
        return self.request(method="get", path=path, params=params)
