# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from ...constants import GUI_PAGE_SIZES, PAGE_SIZE
from ...exceptions import ApiError, NotFoundError
from ...tools import listify
from ..mixins import ChildMixins, PagingMixinsObject


def check_gui_page_size(size=None):
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

    def get_by_tags(self, value, **kwargs):
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

    def get_tags(self, **kwargs):
        """Get all tags for saved queries."""
        rows = self.get(**kwargs)
        tags = [y for x in rows for y in x.get("tags", [])]
        return sorted(list(set(tags)))

    def add(
        self,
        name,
        query=None,
        tags=None,
        description=None,
        fields=None,
        fields_manual=None,
        fields_default=False,
        sort_field=None,
        sort_descending=True,
        column_filters=None,
        gui_page_size=None,
        fields_map=None,
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
            fields_regex=None,
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

    # XXX this isn't in API server yet
    '''
    def update(
        self,
        row,
        add_tags=None,
        remove_tags=None,
        add_fields=None,
        remove_fields=None,
        add_column_filters=None,
        remove_column_filters=None,
        description=None,
        sort_field=None,
        sort_descending=None,
        gui_page_size=None,
        **kwargs,
    ):
        """Update a saved query."""
        new_row = copy.deepcopy(row)
        old_tags = row.get("tags", [])
        old_fields = row["view"]["fields"]
        old_column_filters = row["view"].get("colFilters", {})

        if any([add_fields, remove_fields, sort_field]):
            fields_map = kwargs.get("fields_map") or self.parent.fields.get()

        if add_fields:
            add_fields = self.parent.fields.validate(
                fields=add_fields,
                fields_manual=None,
                fields_regex=None,
                fields_default=False,
                fields_map=fields_map,
            )
            new_fields = old_fields + [x for x in add_fields if x not in old_fields]
            row["view"]["fields"] = new_fields

        if remove_fields:
            remove_fields = self.parent.fields.validate(
                fields=remove_fields,
                fields_manual=None,
                fields_regex=None,
                fields_default=False,
                fields_map=fields_map,
            )
            new_fields = [x for x in old_fields if x not in remove_fields]
            row["view"]["fields"] = new_fields

        if add_tags:
            row["tags"] = old_tags + [x for x in add_tags if x not in old_tags]

        if remove_tags:
            row["tags"] = [x for x in old_tags if x not in remove_tags]

        if description is not None:
            new_row["description"] = description

        if sort_field is not None:
            sort_field = self.parent.fields.get_field_name(
                value=sort_field, fields_map=fields_map
            )
            new_row["view"]["sort"]["field"] = sort_field

        if sort_descending is not None:
            new_row["view"]["sort"]["desc"] = sort_descending

        if add_column_filters:
            new_column_filters = {}
            new_column_filters.update(old_column_filters)
            new_column_filters.update(add_column_filters)
            new_row["view"]["colFilters"] = new_column_filters

        if remove_column_filters:
            new_column_filters = {
                k: v
                for k, v in old_column_filters.items()
                if k not in remove_column_filters
            }
            new_row["view"]["colFilters"] = new_column_filters

        if gui_page_size:
            gui_page_size = check_gui_page_size(gui_page_size=gui_page_size)

        if row == new_row:
            raise ApiError("No changes supplied!")

        self._update(id=row["uuid"], data=new_row)
        kwargs["value"] = row["uuid"]
        return self.get_by_uuid(**kwargs)

    def update_by_name(self, value, **kwargs):
        """Pass."""
        row = self.get_by_name(value=value, **kwargs)
        kwargs["row"] = row
        self.update(**kwargs)
        return row
    '''

    def delete(self, rows):
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

    def delete_by_name(self, value, **kwargs):
        """Delete saved queries returned from get.

        Args:
            rows (:obj:`list` of :obj:`dict`): metadata of saved queries to delete

        Returns:
            :obj:`list` of :obj:`dict`: saved queries deleted
        """
        row = self.get_by_name(value=value, **kwargs)
        self.delete(rows=[row])
        return row

    def _add(self, data):
        """Direct API method to create a saved query.

        Warning:
            Queries created with this method will NOT show the filters in the
            query wizard!

        Returns:
            :obj:`str`: ID of the saved query that was created
        """
        path = self.router.views
        return self.request(method="post", path=path, json=data)

    # XXX this is not in public API, need to add
    # def _update(self, id, data):
    #     """Direct API method to update a saved query.

    #     Args:
    #         id (:obj:`str`): id of saved query to update
    #         data (:obj:`dict`): metadata of saved query to update
    #     """
    #     path = self.router.view_by_id.format(id=id)
    #     return self.request(method="post", path=path, json=data)

    def _delete(self, ids):
        """Direct API method to delete saved queries.

        Args:
            ids (:obj:`list` of :obj:`str`): list of saved query uuid's to delete

        Returns:
            :obj:`str`: empty string
        """
        data = {"ids": listify(ids)}
        path = self.router.views
        return self.request(method="delete", path=path, json=data)

    def _get(self, query=None, row_start=0, page_size=PAGE_SIZE):
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
