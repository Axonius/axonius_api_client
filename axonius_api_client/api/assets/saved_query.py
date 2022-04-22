# -*- coding: utf-8 -*-
"""API for working with saved queries for assets."""
import warnings
from typing import Generator, List, Optional, Union

from ...constants.api import AS_DATACLASS, MAX_PAGE_SIZE
from ...exceptions import (
    AlreadyExists,
    ApiError,
    GuiQueryWizardWarning,
    SavedQueryNotFoundError,
    SavedQueryTagsNotFoundError,
)
from ...tools import check_gui_page_size, coerce_bool, echo_ok, echo_warn, listify
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..mixins import ChildMixins

MODEL = json_api.saved_queries.SavedQuery
MODEL_FOLDER = json_api.saved_queries.Folder
BOTH = Union[dict, MODEL]
MULTI = Union[str, BOTH]
GEN = Generator[BOTH, None, None]


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

    def update_name(self, sq: MULTI, value: str, as_dataclass: bool = AS_DATACLASS) -> BOTH:
        """Update the name of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (str): new name
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)
        self._check_name_exists(value=value)
        sq.set_name(value=value)
        return self._update_handler(sq=sq, as_dataclass=as_dataclass)

    def update_description(
        self, sq: MULTI, value: str, append: bool = False, as_dataclass: bool = AS_DATACLASS
    ) -> BOTH:
        """Update the description of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (str): description to set
            append (bool, optional): append to pre-existing description
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)
        value = f"{sq.description}{value}" if sq.description and append else value
        sq.set_description(value=value)
        return self._update_handler(sq=sq, as_dataclass=as_dataclass)

    def update_page_size(self, sq: MULTI, value: int, as_dataclass: bool = AS_DATACLASS) -> BOTH:
        """Update the GUI page size of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (int): page size to set
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)
        sq.page_size = value
        return self._update_handler(sq=sq, as_dataclass=as_dataclass)

    def update_sort(
        self,
        sq: MULTI,
        field: Optional[str] = None,
        descending: bool = True,
        as_dataclass: bool = AS_DATACLASS,
    ) -> BOTH:
        """Update the sort of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            field (Optional[str], optional): field to sort results on
            descending (bool, optional): sort descending or ascending
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)

        if isinstance(field, str) and field.strip():
            field = self.parent.fields.get_field_name(value=field)
        else:
            field = ""

        sq.sort_field = field
        sq.sort_descending = descending
        return self._update_handler(sq=sq, as_dataclass=as_dataclass)

    def update_tags(
        self,
        sq: MULTI,
        value: Union[str, List[str]],
        remove: bool = False,
        append: bool = False,
        as_dataclass: bool = AS_DATACLASS,
    ) -> BOTH:
        """Update the tags of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (Union[str, List[str]]): tags to set
            remove (bool, optional): remove tags in value from saved query tags
            append (bool, optional): append tags in value to pre-existing saved query tags
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        value = listify(value)
        if not all([isinstance(x, str) and x.strip() for x in value]):
            raise ApiError(f"Value must be a list of non-empty strings, not {value!r}")

        sq = self.get_by_multi(sq=sq, as_dataclass=True)

        if remove:
            value = [x for x in sq.tags if x not in value]
        elif append:
            value = sq.tags + [x for x in value if x not in sq.tags]

        sq.set_tags(value=value)
        return self._update_handler(sq=sq, as_dataclass=as_dataclass)

    def update_always_cached(
        self, sq: MULTI, value: bool, as_dataclass: bool = AS_DATACLASS
    ) -> BOTH:
        """Update the always_cached flag of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (bool): should the saved query always being cached
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        return self._update_flag(
            attr="always_cached", sq=sq, value=value, as_dataclass=as_dataclass
        )

    def update_private(self, sq: MULTI, value: bool, as_dataclass: bool = AS_DATACLASS) -> BOTH:
        """Update the private flag of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (bool): should the saved query be private
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        return self._update_flag(attr="private", sq=sq, value=value, as_dataclass=as_dataclass)

    def update_fields(
        self,
        sq: MULTI,
        fields: Optional[Union[List[str], str]] = None,
        fields_manual: Optional[Union[List[str], str]] = None,
        fields_regex: Optional[Union[List[str], str]] = None,
        fields_regex_root_only: bool = True,
        fields_fuzzy: Optional[Union[List[str], str]] = None,
        fields_default: bool = False,
        fields_root: Optional[str] = None,
        remove: bool = False,
        append: bool = False,
        as_dataclass: bool = AS_DATACLASS,
    ) -> BOTH:
        """Update the tags of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            fields (Optional[Union[List[str], str]], optional): fields
            fields_manual (Optional[Union[List[str], str]], optional): fields fully qualified
            fields_regex (Optional[Union[List[str], str]], optional): fields via regex
            fields_fuzzy (Optional[Union[List[str], str]], optional): fields via fuzzy
            fields_default (bool, optional): Include default fields
            fields_root (Optional[str], optional): fields via root
            remove (bool, optional): remove supplied fields from saved query fields
            append (bool, optional): append supplied fields in value to pre-existing saved query
                fields
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)

        value = self.parent.fields.validate(
            fields=fields,
            fields_manual=fields_manual,
            fields_regex=fields_regex,
            fields_default=fields_default,
            fields_root=fields_root,
            fields_fuzzy=fields_fuzzy,
            fields_regex_root_only=fields_regex_root_only,
        )

        if remove:
            value = [x for x in sq.fields if x not in value]
        elif append:
            value = sq.fields + [x for x in value if x not in sq.fields]

        sq.fields = value
        return self._update_handler(sq=sq, as_dataclass=as_dataclass)

    def update_query(
        self,
        sq: MULTI,
        query: Optional[str] = None,
        expressions: Optional[List[str]] = None,
        wiz_entries: Optional[Union[str, List[dict]]] = None,
        append: bool = False,
        append_and_flag: bool = False,
        append_not_flag: bool = False,
        as_dataclass: bool = AS_DATACLASS,
        **kwargs,
    ) -> BOTH:
        """Update the query of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            query (Optional[str]], optional): previously generated query
            expressions (Optional[List[str]], optional): Expressions for GUI Query Wizard
            wiz_entries (Optional[Union[str, List[dict]]]): API query wizard entries to parse
                into query and GUI query wizard expressions
            append (bool, optional): append query to pre-existing query
            append_and_flag (bool, optional): use and instead of or for appending query
            append_not_flag (bool, optional): use 'and not'/'or not' for appending query
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)

        wiz_parsed: dict = self.parent.get_wiz_entries(wiz_entries=wiz_entries)

        if wiz_parsed:
            query = wiz_parsed["query"]
            expressions = wiz_parsed["expressions"]

        if append:
            if not isinstance(query, str) or (isinstance(query, str) and not query.strip()):
                raise ApiError(f"No query supplied to append to Saved Query:\n{sq}")

            operand = "and" if append_and_flag else "or"
            join = f"{operand} not" if append_not_flag else f"{operand}"
            query = f"{sq.query} {join} {query}"

            if isinstance(expressions, list) and expressions:
                if isinstance(sq.expressions, list) and sq.expressions:
                    first = expressions[0]
                    first["not"] = coerce_bool(append_not_flag)
                    first["logicOp"] = operand
                    first["filter"] = f"{join} {first['filter']}"
                    expressions = sq.expressions + expressions
            else:
                msg = "\n".join(
                    [
                        f"Appending query {query!r} with no expressions",
                        "GUI query wizard will not display properly!",
                        f"{sq}",
                    ]
                )
                warnings.warn(message=msg, category=GuiQueryWizardWarning)

        sq.query = query
        sq.query_expr = query
        if isinstance(expressions, list):
            sq.expressions = expressions
        elif not append:
            msg = "\n".join(
                [
                    f"Updating query {query!r} with no expressions",
                    "GUI query wizard will not display properly!",
                    f"{sq}",
                ]
            )
            warnings.warn(message=msg, category=GuiQueryWizardWarning)

        return self._update_handler(sq=sq, as_dataclass=as_dataclass)

    def copy(
        self,
        sq: MULTI,
        name: str,
        private: bool = False,
        asset_scope: bool = False,
        always_cached: bool = False,
        as_dataclass: bool = AS_DATACLASS,
    ) -> BOTH:
        """Create a copy of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            name (str): name to use for new sq
            private (bool, optional): Set new sq as private
            asset_scope (bool, optional): Set new sq as asset scope query
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        create_model = json_api.saved_queries.SavedQueryCreate
        self._check_name_exists(value=name)
        sq = self.get_by_multi(sq=sq, as_dataclass=True)
        sq_create = {k: v for k, v in sq.to_dict().items() if k in create_model._get_field_names()}
        to_add = create_model.new_from_dict(sq_create)
        to_add.private = coerce_bool(private)
        to_add.asset_scope = coerce_bool(asset_scope)
        to_add.always_cached = coerce_bool(always_cached)
        to_add.set_name(value=name)
        added = self._add_from_dataclass(obj=to_add)
        return self.get_by_multi(sq=added, as_dataclass=as_dataclass)

    def get_by_multi(
        self, sq: MULTI, as_dataclass: bool = AS_DATACLASS, asset_scopes: bool = False, **kwargs
    ) -> BOTH:
        """Get a saved query by name or uuid.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            as_dataclass (bool, optional): Return saved query dataclass instead of dict
            **kwargs: passed to :meth:`get`

        Returns:
            BOTH: saved query dataclass or dict

        Raises:
            ApiError: if sq is not a str, saved query dict, or saved query dataclass
            SavedQueryNotFoundError: If no sq found with name or uuid from value
        """
        if isinstance(sq, str):
            name = sq
            uuid = sq
        elif isinstance(sq, dict) and "uuid" in sq and "name" in sq:
            name = sq["name"]
            uuid = sq["uuid"]
        elif isinstance(sq, MODEL):
            name = sq.name
            uuid = sq.uuid
        else:
            raise ApiError(f"Unknown type {type(sq)}, must be a str, dict, or {MODEL}")

        searches = [name, uuid]
        sq_objs = self.get(as_dataclass=True, **kwargs)
        details = f"name={name!r} or uuid={uuid!r}"

        if asset_scopes:
            sq_objs = [x for x in sq_objs if x.asset_scope]
            details = f"{details} and is asset scope query"

        for sq_obj in sq_objs:
            checks = (
                [sq_obj.name, sq_obj.uuid]
                if isinstance(sq_obj, MODEL)
                else [sq_obj.get("name"), sq_obj.get("uuid")]
            )
            if any([x in checks for x in searches]):
                return sq_obj if as_dataclass else sq_obj.to_dict()

        raise SavedQueryNotFoundError(sqs=sq_objs, details=details)

    def get_by_name(self, value: str, as_dataclass: bool = AS_DATACLASS) -> BOTH:
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
            value (str): name of saved query
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Raises:
            SavedQueryNotFoundError: if no saved query found with name of value

        Returns:
            BOTH: saved query dataclass or dict

        """
        sqs = self.get(as_dataclass=True)

        for sq in sqs:
            if value == sq.name:
                return sq if as_dataclass else sq.to_dict()

        raise SavedQueryNotFoundError(sqs=sqs, details=f"name={value!r}")

    def get_by_uuid(self, value: str, as_dataclass: bool = AS_DATACLASS) -> BOTH:
        """Get a saved query by uuid.

        Examples:
            Get a saved query by uuid

            >>> sq = apiobj.saved_query.get_by_uuid(value="5f76721ce4557d5cba93f59e")

        Args:
            value (str): uuid of saved query
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Raises:
            SavedQueryNotFoundError: if no saved query found with uuid of value

        Returns:
            BOTH: saved query dataclass or dict
        """
        sqs = self.get(as_dataclass=True)

        for sq in sqs:
            if value == sq.uuid:
                return sq if as_dataclass else sq.to_dict()

        raise SavedQueryNotFoundError(sqs=sqs, details=f"uuid={value!r}")

    def get_by_tags(
        self, value: Union[str, List[str]], as_dataclass: bool = AS_DATACLASS
    ) -> List[BOTH]:
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
            value (Union[str, List[str]]): list of tags
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Raises:
            SavedQueryTagsNotFoundError: if no saved queries found with supplied tags

        Returns:
            List[BOTH]: list of saved query dataclass or dict containing any tags in value
        """
        value = listify(value)
        sqs = self.get(as_dataclass=True)

        found = []
        valid = set()

        for sq in sqs:
            valid.update(sq.tags)
            if any([tag in value for tag in sq.tags]):
                found.append(sq)

        if not found:
            raise SavedQueryTagsNotFoundError(value=value, valid=valid)
        return found if as_dataclass else [x.to_dict() for x in found]

    def get_tags(self) -> List[str]:
        """Get all tags for saved queries.

        Examples:
            Get all known tags for all saved queries

            >>> tags = apiobj.saved_query.get_tags()
            >>> len(tags)
            19

        Returns:
            List[str]: list of all tags in use
        """
        tags = []
        for sq in self.get(as_dataclass=True):
            tags += [x for x in sq.tags if x not in tags]
        return tags

    def get(self, generator: bool = False, **kwargs) -> Union[GEN, List[BOTH]]:
        """Get all saved queries.

        Examples:
            Get all saved queries

            >>> sqs = apiobj.saved_query.get()
            >>> len(sqs)
            39

        Args:
            generator: return an iterator

        Yields:
            GEN: if generator = True, saved query dataclass or dict

        Returns:
            List[BOTH]: if generator = False, list of saved query dataclass or dict

        """
        if "sqs" in kwargs:
            return kwargs["sqs"]

        gen = self.get_generator(**kwargs)

        if generator:
            return gen

        return list(gen)

    def get_generator(self, as_dataclass: bool = AS_DATACLASS) -> GEN:
        """Get Saved Queries using a generator.

        Args:
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Yields:
            GEN: saved query dataclass or dict
        """
        offset = 0

        while True:
            rows = self._get(offset=offset)
            offset += len(rows)

            if not rows:
                break

            for row in rows:
                yield row if as_dataclass else row.to_dict()

    def add(self, as_dataclass: bool = AS_DATACLASS, **kwargs) -> BOTH:
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
            as_dataclass (bool, optional): return saved query dataclass or dict
            **kwargs: passed to :meth:`build_add_model`

        Returns:
            BOTH: saved query dataclass or dict

        """
        create_obj = self.build_add_model(**kwargs)
        added = self._add_from_dataclass(obj=create_obj)
        return self.get_by_uuid(value=added.id, as_dataclass=as_dataclass)

    def build_add_model(
        self,
        name: str,
        query: Optional[str] = None,
        wiz_entries: Optional[Union[List[dict], List[str], dict, str]] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        expressions: Optional[List[str]] = None,
        fields: Optional[Union[List[str], str]] = None,
        fields_manual: Optional[Union[List[str], str]] = None,
        fields_regex: Optional[Union[List[str], str]] = None,
        fields_regex_root_only: bool = True,
        fields_fuzzy: Optional[Union[List[str], str]] = None,
        fields_default: bool = True,
        fields_root: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_descending: bool = True,
        column_filters: Optional[dict] = None,
        gui_page_size: Optional[int] = None,
        private: bool = False,
        always_cached: bool = False,
        asset_scope: bool = False,
        # WIP: folders
        # folder_path: Optional[Union[str, List[str]]] = None,
        # folder_id: Optional[str] = None,
        **kwargs,
    ) -> json_api.saved_queries.SavedQueryCreate:
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
            query: query built by GUI or API query wizard
            wiz_entries (Optional[Union[str, List[dict]]]): API query wizard entries to parse
                into query and GUI query wizard expressions
            tags (Optional[List[str]], optional): list of tags
            expressions (Optional[List[str]], optional): Expressions for GUI Query Wizard
            fields: fields to return for each asset (will be validated)
            fields_manual: fields to return for each asset (will NOT be validated)
            fields_regex: regex of fields to return for each asset
            fields_fuzzy: string to fuzzy match of fields to return for each asset
            fields_default: include the default fields defined in the parent asset object
            fields_root: include all fields of an adapter that are not complex sub-fields
            sort_field: sort the returned assets on a given field
            sort_descending: reverse the sort of the returned assets
            column_filters: NOT_SUPPORTED
            gui_page_size: show N rows per page in GUI
            private: make this saved query private to current user
            always_cached: always keep this query cached
            asset_scope: make this query an asset scope query

        Returns:
            json_api.saved_queries.SavedQueryCreate: saved query dataclass to create

        """
        # WIP: folders
        # if isinstance(folder_path, str):
        #     folders = self.get_folders()
        #     folder = folders.search(value=folder_path)
        #     folder_id = folder.id

        asset_scope = coerce_bool(asset_scope)
        private = coerce_bool(private)
        always_cached = coerce_bool(always_cached)
        query_expr: Optional[str] = kwargs.get("query_expr", None) or query
        wiz_parsed: dict = self.parent.get_wiz_entries(wiz_entries=wiz_entries)

        if wiz_parsed:
            query = wiz_parsed["query"]
            query_expr = query
            expressions = wiz_parsed["expressions"]

        gui_page_size = check_gui_page_size(size=gui_page_size)

        fields = self.parent.fields.validate(
            fields=fields,
            fields_manual=fields_manual,
            fields_regex=fields_regex,
            fields_default=fields_default,
            fields_root=fields_root,
            fields_fuzzy=fields_fuzzy,
            fields_regex_root_only=fields_regex_root_only,
            fields_error=True,
        )

        if sort_field:
            sort_field = self.parent.fields.get_field_name(value=sort_field)

        view = {}
        view["query"] = {}
        view["query"]["filter"] = query or ""
        view["query"]["expressions"] = expressions or []
        view["query"]["search"] = None  # TBD
        view["query"]["meta"] = {}  # TBD
        view["query"]["meta"]["enforcementFilter"] = None  # TBD
        view["query"]["meta"]["uniqueAdapters"] = False  # TBD

        if query_expr:
            view["query"]["onlyExpressionsFilter"] = query_expr

        view["sort"] = {}
        view["sort"]["desc"] = sort_descending
        view["sort"]["field"] = sort_field or ""
        view["fields"] = fields
        view["pageSize"] = gui_page_size
        return json_api.saved_queries.SavedQueryCreate.new_from_kwargs(
            name=name,
            description=description,
            view=view,
            private=private,
            always_cached=always_cached,
            asset_scope=asset_scope,
            tags=tags,
            # WIP: folders
            # folder_id=folder_id,
        )

    def delete_by_name(self, value: str, as_dataclass: bool = AS_DATACLASS) -> BOTH:
        """Delete a saved query by name.

        Examples:
            Delete the saved query by name

            >>> deleted = apiobj.saved_query.delete_by_name(name="test")

        Args:
            value (str): name of saved query to delete
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        sq = self.get_by_name(value=value, as_dataclass=True)
        self._delete(uuid=sq.uuid)
        return sq if as_dataclass else sq.to_dict()

    def delete(
        self,
        rows: Union[List[MULTI], MULTI],
        errors: bool = True,
        refetch: bool = True,
        as_dataclass: bool = AS_DATACLASS,
        **kwargs,
    ) -> List[BOTH]:
        """Delete saved queries.

        Args:
            rows (Union[List[MULTI], MULTI]): str or list of str with name, str or list of str
                with uuid, saved query dict or list of dict, or saved query dataclass or list
                of dataclass
            errors (bool, optional): Raise errors if SQ not found or other error
            refetch (bool, optional): refetch dataclass objects before deleting SQ
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            List[BOTH]: list of saved query dataclass or dict that were deleted

        """
        do_echo = kwargs.get("do_echo", False)
        sqs = self.get(as_dataclass=True)
        deleted = []
        for row in listify(rows):
            try:
                sq = row
                if not isinstance(row, MODEL) or refetch:
                    sq = self.get_by_multi(sq=row, as_dataclass=True, sqs=sqs)

                if sq not in deleted:
                    self._delete(uuid=sq.uuid)
                    msg = f"Saved Query deleted name={sq.name!r}, uuid={sq.uuid}"
                    echo_ok(msg=msg) if do_echo else self.LOG.info(msg)
                    deleted.append(sq)

            except ApiError as exc:
                if errors:
                    raise

                msg = f"Saved query unable to be deleted {row!r}, error:\n{exc}"
                echo_warn(msg=msg) if do_echo else self.LOG.warning(msg)
                continue

        return deleted if as_dataclass else [x.to_dict() for x in deleted]

    def _update_flag(
        self, attr: str, sq: MULTI, value: bool, as_dataclass: bool = AS_DATACLASS
    ) -> BOTH:
        """Update a boolean flag for a SQ.

        Args:
            attr (str): attribute name
            sq (MULTI): saved query to update
            value (bool): value to set to attr
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)
        value = coerce_bool(obj=value, errmsg=f"{attr} requires a valid boolean")
        setattr(sq, attr, value)
        return self._update_handler(sq=sq, as_dataclass=as_dataclass)

    def _update_handler(self, sq: MODEL, as_dataclass: bool = AS_DATACLASS) -> BOTH:
        """Update a SQ.

        Args:
            sq (MULTI): saved query to update
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            BOTH: saved query dataclass or dict
        """
        ret = self._update(
            uuid=sq.uuid,
            name=sq.name,
            view=sq.view,
            description=sq.description,
            tags=sq.tags,
            private=sq.private,
            always_cached=sq.always_cached,
            asset_scope=sq.asset_scope,
        )
        return ret if as_dataclass else ret.to_dict()

    def _update_from_dataclass(
        self, obj: json_api.saved_queries.SavedQueryCreate, uuid: str
    ) -> MODEL:
        """Direct API method to update a saved query.

        Args:
            obj (json_api.saved_queries.SavedQueryCreate): pre-created dataclass

        Returns:
            MODEL: saved query dataclass
        """
        return self._update(
            uuid=uuid,
            **obj.get_attrs(),
        )

    def _update(
        self,
        uuid: str,
        name: str,
        view: dict,
        description: str = "",
        tags: Optional[List[str]] = None,
        private: bool = False,
        always_cached: bool = False,
        asset_scope: bool = False,
        # WIP: folders
        # folder_id: Optional[str] = None,
    ) -> MODEL:
        """Direct API method to update a saved query.

        Args:
            uuid (str): UUID of SQ to update
            name (str): name to set
            view (dict): view object to set
            description (str, optional): description to set
            tags (Optional[List[str]], optional): tags to set
            private (bool, optional): set sq as private or public
            always_cached (bool, optional): set sq as always cached
            asset_scope (bool, optional): set sq as asset scope query

        Returns:
            MODEL: saved query dataclass
        """
        api_endpoint = ApiEndpoints.saved_queries.update
        request_obj = api_endpoint.load_request(
            name=name,
            view=view,
            description=description,
            always_cached=always_cached,
            private=private,
            tags=tags or [],
            asset_scope=asset_scope,
            # WIP: folders
            # folder_id=folder_id,
        )
        return api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            asset_type=self.parent.ASSET_TYPE,
            uuid=uuid,
        )

    def _add_from_dataclass(self, obj: json_api.saved_queries.SavedQueryCreate) -> MODEL:
        """Direct API method to create a saved query.

        Args:
            obj (json_api.saved_queries.SavedQueryCreate): pre-created dataclass

        Returns:
            MODEL: saved query dataclass
        """
        return self._add(**obj.get_attrs())

    def _add(
        self,
        name: str,
        view: dict,
        description: Optional[str] = "",
        tags: Optional[List[str]] = None,
        private: bool = False,
        always_cached: bool = False,
        asset_scope: bool = False,
        # WIP: folders
        # folder_id: Optional[str] = None,
    ) -> MODEL:
        """Direct API method to create a saved query.

        Args:

            name (str): name to set
            view (dict): view object to set
            description (str, optional): description to set
            tags (Optional[List[str]], optional): tags to set
            private (bool, optional): set sq as private or public
            always_cached (bool, optional): set sq as always cached
            asset_scope (bool, optional): set sq as asset scope query

        Returns:
            MODEL: saved query dataclass
        """
        api_endpoint = ApiEndpoints.saved_queries.create
        request_obj = api_endpoint.load_request(
            name=name,
            view=view,
            description=description,
            always_cached=always_cached,
            private=private,
            tags=tags or [],
            asset_scope=asset_scope,
            # WIP: folders
            # folder_id=folder_id,
        )
        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=self.parent.ASSET_TYPE
        )

    def _delete(self, uuid: str) -> json_api.generic.Metadata:
        """Direct API method to delete saved queries.

        Args:
            uuid (str): uuid of SQ to delete

        Returns:
            json_api.generic.Metadata: Metadata object containing UUID of deleted SQ
        """
        api_endpoint = ApiEndpoints.saved_queries.delete
        request_obj = api_endpoint.load_request()
        return api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            asset_type=self.parent.ASSET_TYPE,
            uuid=uuid,
        )

    def _get(self, limit: int = MAX_PAGE_SIZE, offset: int = 0) -> List[MODEL]:
        """Direct API method to get all users.

        Args:
            limit (int, optional): limit to N rows per page
            offset (int, optional): start at row N

        Returns:
            List[MODEL]: list of saved query dataclass
        """
        api_endpoint = ApiEndpoints.saved_queries.get
        request_obj = api_endpoint.load_request(page={"limit": limit, "offset": offset})
        return api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=self.parent.ASSET_TYPE
        )

    def _check_name_exists(self, value: str):
        """Check if a SQ already exists with a given name.

        Args:
            value (str): Name to check

        Raises:
            AlreadyExists: if SQ with name of value found
        """
        try:
            sq = self.get_by_name(value=value, as_dataclass=True)
            raise AlreadyExists(f"Saved query with name or uuid of {value!r} already exists:\n{sq}")
        except SavedQueryNotFoundError:
            return

    # WIP: folders
    '''
    def _get_folders(self) -> json_api.saved_queries.FoldersResponse:
        """Direct API method to get all folders.

        Returns:
            json_api.saved_queries.FoldersResponse: API response model
        """
        api_endpoint = ApiEndpoints.saved_queries.get_folders
        return api_endpoint.perform_request(http=self.auth.http)

    def folder_get(self) -> json_api.saved_queries.FoldersResponse:
        """Direct API method to get all folders.

        Returns:
            json_api.saved_queries.FoldersResponse: API response model
        """
        return self._get_folders()

    def folder_get_path(self, value: Union[MODEL_FOLDER, str, List[str]]) -> MODEL_FOLDER:
        """Pass."""
        if isinstance(value, MODEL_FOLDER):
            return value
        folders = self.folder_get()
        return folders.search(value=value)

    # folder_get(value: Optional[str])
    # folder_get_path(value: Union[Folder, str, List[str]])

    # resolve_folder_path(folder_path, folder_id)
    # folder_create(path: Union[Folder, str], name: str)
    #   - err on read only
    # folder_delete(path: Union[Folder, str])
    #   - err on root/read only
    # folder_rename(path: Folder/str, name: str)
    #   - err on root/read only
    # folder_move(from_path: Union[Folder, str, List[str]], to_path: Union[Folder, str, List[str] )
    #   - err on root/read only
    '''
