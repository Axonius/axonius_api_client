# -*- coding: utf-8 -*-
"""API for working with saved queries for assets."""
import datetime
import typing as t
import warnings

from cachetools import TTLCache, cached

from ...constants.api import AS_DATACLASS
from ...constants.ctypes import PatternLikeListy
from ...exceptions import (
    AlreadyExists,
    ApiError,
    GuiQueryWizardWarning,
    SavedQueryNotFoundError,
    SavedQueryTagsNotFoundError,
)
from ...tools import check_gui_page_size, coerce_bool, echo_ok, echo_warn, listify
from ..api_endpoints import ApiEndpoints
from ..folders import FoldersQueries
from ..json_api import saved_queries as models
from ..json_api.folders.base import FolderDefaults
from ..json_api.folders.queries import FolderModel, FoldersModel
from ..json_api.generic import ListValueSchema, Metadata
from ..json_api.paging_state import LOG_LEVEL_API, PAGE_SIZE, PagingState
from ..mixins import ChildMixins

MULTI = t.Union[str, dict, models.SavedQuery]
CACHE_TAGS = TTLCache(maxsize=1024, ttl=60)
CACHE_RUN_BY = TTLCache(maxsize=1024, ttl=60)
CACHE_RUN_FROM = TTLCache(maxsize=1024, ttl=60)
CACHE_GET = TTLCache(maxsize=1024, ttl=60)


class SavedQuery(ChildMixins):
    """API object for working with saved queries for the parent asset type.

    Examples:
        Create a ``client`` using :obj:`axonius_api_client.connect.Connect` and assume
        ``apiobj`` is either ``client.devices`` or ``client.users``

        >>> import axonius_api_client as axonapi
        >>> connect_args: dict = axonapi.get_env_connect()
        >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
        >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
        >>>       # or client.users or client.vulnerabilities

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

    @property
    def folders(self) -> FoldersQueries:
        """Get the folders api for this object type."""
        # noinspection PyUnresolvedReferences
        return self.auth.http.CLIENT.folders.queries

    def update_folder(
        self,
        sq: MULTI,
        folder: t.Union[str, FolderModel],
        as_dataclass: bool = AS_DATACLASS,
        create: bool = FolderDefaults.create_action,
        echo: bool = FolderDefaults.echo_action,
    ) -> t.Union[dict, models.SavedQuery]:
        """Update the name of a Saved Query.

        Args:
            sq: str with name or uuid, or saved query dict or dataclass
            folder: new name
            as_dataclass: Return saved query dataclass instead of dict
            create: create folder if it does not exist
            echo: echo status to stdout

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)
        updated_obj = sq.move(
            folder=folder,
            create=create,
            echo=echo,
            refresh=False,
        )
        return updated_obj if as_dataclass else updated_obj.to_dict()

    def update_name(
        self, sq: MULTI, value: str, as_dataclass: bool = AS_DATACLASS
    ) -> t.Union[dict, models.SavedQuery]:
        """Update the name of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (str): new name
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)
        self._check_name_exists(value=value)
        sq.set_name(value=value)
        return self._update_handler(sq=sq, as_dataclass=as_dataclass)

    def update_description(
        self, sq: MULTI, value: str, append: bool = False, as_dataclass: bool = AS_DATACLASS
    ) -> t.Union[dict, models.SavedQuery]:
        """Update the description of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (str): description to set
            append (bool, optional): append to pre-existing description
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)
        return sq.update_description(value=value, append=append, as_dataclass=as_dataclass)

    def update_page_size(
        self, sq: MULTI, value: int, as_dataclass: bool = AS_DATACLASS
    ) -> t.Union[dict, models.SavedQuery]:
        """Update the GUI page size of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (int): page size to set
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)
        sq.page_size = value
        return self._update_handler(sq=sq, as_dataclass=as_dataclass)

    def update_sort(
        self,
        sq: MULTI,
        field: t.Optional[str] = None,
        descending: bool = True,
        as_dataclass: bool = AS_DATACLASS,
    ) -> t.Union[dict, models.SavedQuery]:
        """Update the sort field of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            field (t.Optional[str], optional): field to sort results on
            descending (bool, optional): sort descending or ascending
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
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
        value: t.Union[str, t.List[str]],
        remove: bool = False,
        append: bool = False,
        as_dataclass: bool = AS_DATACLASS,
    ) -> t.Union[dict, models.SavedQuery]:
        """Update the tags of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (t.Union[str, t.List[str]]): tags to set
            remove (bool, optional): remove tags in value from saved query tags
            append (bool, optional): append tags in value to pre-existing saved query tags
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
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
    ) -> t.Union[dict, models.SavedQuery]:
        """Update the always_cached flag of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (bool): should the saved query always being cached
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
        """
        return self._update_flag(
            attr="always_cached", sq=sq, value=value, as_dataclass=as_dataclass
        )

    def update_private(
        self, sq: MULTI, value: bool, as_dataclass: bool = AS_DATACLASS
    ) -> t.Union[dict, models.SavedQuery]:
        """Update the private flag of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            value (bool): should the saved query be private
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
        """
        return self._update_flag(attr="private", sq=sq, value=value, as_dataclass=as_dataclass)

    def update_fields(
        self,
        sq: MULTI,
        fields: t.Optional[t.Union[t.List[str], str]] = None,
        fields_manual: t.Optional[t.Union[t.List[str], str]] = None,
        fields_regex: t.Optional[t.Union[t.List[str], str]] = None,
        fields_regex_root_only: bool = True,
        fields_fuzzy: t.Optional[t.Union[t.List[str], str]] = None,
        fields_default: bool = False,
        fields_root: t.Optional[str] = None,
        remove: bool = False,
        append: bool = False,
        as_dataclass: bool = AS_DATACLASS,
    ) -> t.Union[dict, models.SavedQuery]:
        """Update the tags of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            fields (t.Optional[t.Union[t.List[str], str]], optional): fields
            fields_manual (t.Optional[t.Union[t.List[str], str]], optional): fields fully qualified
            fields_regex (t.Optional[t.Union[t.List[str], str]], optional): fields via regex
            fields_fuzzy (t.Optional[t.Union[t.List[str], str]], optional): fields via fuzzy
            fields_default (bool, optional): Include default fields
            fields_root (t.Optional[str], optional): fields via root
            fields_regex_root_only (bool, optional): only match root fields in fields_regex
            remove (bool, optional): remove supplied fields from saved query fields
            append (bool, optional): append supplied fields in value to pre-existing saved query
                fields
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
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

    # noinspection PyUnusedLocal
    def update_query(
        self,
        sq: MULTI,
        query: t.Optional[str] = None,
        expressions: t.Optional[t.List[str]] = None,
        wiz_entries: t.Optional[t.Union[str, t.List[dict]]] = None,
        append: bool = False,
        append_and_flag: bool = False,
        append_not_flag: bool = False,
        as_dataclass: bool = AS_DATACLASS,
        **kwargs,
    ) -> t.Union[dict, models.SavedQuery]:
        """Update the query of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            query (t.Optional[str]], optional): previously generated query
            expressions (t.Optional[t.List[str]], optional): Expressions for GUI Query Wizard
            wiz_entries (t.Optional[t.Union[str, t.List[dict]]]): API query wizard entries to parse
                into query and GUI query wizard expressions
            append (bool, optional): append query to pre-existing query
            append_and_flag (bool, optional): use and instead of or for appending query
            append_not_flag (bool, optional): use 'and not'/'or not' for appending query
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
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

        query = query or ""
        sq.query = query
        sq.query_expr = query
        if isinstance(expressions, list):
            sq.expressions = expressions
        elif not append and query:
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
        as_dataclass: bool = AS_DATACLASS,
        always_cached: bool = False,
        folder: t.Optional[t.Union[str, FolderModel]] = None,
        create: bool = FolderDefaults.create_action,
        echo: bool = FolderDefaults.echo,
    ) -> t.Union[dict, models.SavedQuery]:
        """Create a copy of a Saved Query.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            name (str): name to use for new sq
            private (bool, optional): Set new sq as private
            asset_scope (bool, optional): Set new sq as asset scope query
            as_dataclass (bool, optional): Return saved query dataclass instead of dict
            always_cached (bool, optional): Set new sq as always cached
            folder (t.Optional[t.Union[str, FolderModel]], optional): Folder to create new sq in
            create (bool, optional): Create folder if it doesn't exist
            echo (bool, optional): Echo API response

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
        """
        existing = self.get_by_multi(sq=sq, as_dataclass=True)
        created_obj = existing.copy(
            folder=folder,
            create=create,
            name=name,
            echo=echo,
            private=private,
            asset_scope=asset_scope,
            always_cached=always_cached,
        )
        return created_obj if as_dataclass else created_obj.to_dict()

    def get_by_multi(
        self,
        sq: MULTI,
        as_dataclass: bool = AS_DATACLASS,
        asset_scopes: bool = False,
        cache: bool = False,
        **kwargs,
    ) -> t.Union[dict, models.SavedQuery]:
        """Get a saved query by name or uuid.

        Args:
            sq (MULTI): str with name or uuid, or saved query dict or dataclass
            as_dataclass (bool, optional): Return saved query dataclass instead of dict
            asset_scopes (bool, optional): Only search asset scope queries
            cache (bool, optional): Get cached results
            **kwargs: passed to :meth:`get`

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict

        Raises:
            ApiError: if sq is not a str, saved query dict, or saved query dataclass
            models.SavedQueryNotFoundError: If no sq found with name or uuid from value
        """
        if isinstance(sq, str):
            name = sq
            uuid = sq
        elif isinstance(sq, dict) and "uuid" in sq and "name" in sq:
            name = sq["name"]
            uuid = sq["uuid"]
        elif isinstance(sq, models.SavedQuery):
            name = sq.name
            uuid = sq.uuid
        else:
            raise ApiError(f"Unknown type {type(sq)}, must be a str, dict, or {models.SavedQuery}")

        searches = [name, uuid]
        get_method = self.get_cached if cache else self.get
        sq_objs = get_method(as_dataclass=True, **kwargs)
        details = f"name={name!r} or uuid={uuid!r}"

        if asset_scopes:
            sq_objs = [x for x in sq_objs if x.asset_scope]
            details = f"{details} and is asset scope query"

        for sq_obj in sq_objs:
            checks = (
                [sq_obj.name, sq_obj.uuid]
                if isinstance(sq_obj, models.SavedQuery)
                else [sq_obj.get("name"), sq_obj.get("uuid")]
            )
            if any([x in checks for x in searches]):
                return sq_obj if as_dataclass else sq_obj.to_dict()

        raise SavedQueryNotFoundError(sqs=sq_objs, details=details)

    def get_by_name(
        self, value: str, as_dataclass: bool = AS_DATACLASS, **kwargs
    ) -> t.Union[dict, models.SavedQuery]:
        """Get a saved query by name.

        Examples:
            Get a saved query by name

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> data = apiobj.saved_query.get_by_name(name="test")
            >>> data['tags']
            ['Unmanaged Devices']
            >>> data['description'][:80]
            'Devices that have been seen by at least one agent or at least one endpoint manag'
            >>> data['view']['fields']
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
            >>> data['view']['query']['filter'][:80]
            '(specific_data.data.adapter_properties == "Agent") or (specific_data.data.adapte'

        Args:
            value (str): name of saved query
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Raises:
            SavedQueryNotFoundError: if no saved query found with name of value

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict

        """
        sqs = self.get(as_dataclass=True, **kwargs)

        for sq in sqs:
            if value == sq.name:
                return sq if as_dataclass else sq.to_dict()

        raise SavedQueryNotFoundError(sqs=sqs, details=f"name={value!r}")

    def get_by_uuid(
        self, value: str, as_dataclass: bool = AS_DATACLASS, **kwargs
    ) -> t.Union[dict, models.SavedQuery]:
        """Get a saved query by uuid.

        Examples:
            Get a saved query by uuid

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> data = apiobj.saved_query.get_by_uuid(value="5f76721ce4557d5cba93f59e")

        Args:
            value (str): uuid of saved query
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Raises:
            SavedQueryNotFoundError: if no saved query found with uuid of value

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
        """
        sqs = self.get(as_dataclass=True, **kwargs)

        for sq in sqs:
            if value == sq.uuid:
                return sq if as_dataclass else sq.to_dict()

        raise SavedQueryNotFoundError(sqs=sqs, details=f"uuid={value!r}")

    def get_by_tags(
        self, value: t.Union[str, t.List[str]], as_dataclass: bool = AS_DATACLASS, **kwargs
    ) -> t.List[t.Union[dict, models.SavedQuery]]:
        """Get saved queries by tags.

        Examples:
            Get all saved queries with tagged with 'AD'
            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> data = apiobj.saved_query.get_by_tags('AD')
            >>> len(data)
            2

            Get all saved queries with tagged with 'AD' or 'AWS'
            >>> data = apiobj.saved_query.get_by_tags(['AD', 'AWS'])
            >>> len(data)
            5

        Args:
            value (t.Union[str, t.List[str]]): list of tags
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Raises:
            SavedQueryTagsNotFoundError: if no saved queries found with supplied tags

        Returns:
            t.List[t.Union[dict, models.SavedQuery]]: list of saved query dataclass or dict
                containing any tags in value
        """
        value = listify(value)
        sqs = self.get(as_dataclass=True, **kwargs)

        found = []
        valid = set()

        for sq in sqs:
            valid.update(sq.tags)
            if any([tag in value for tag in sq.tags]):
                found.append(sq)

        if not found:
            raise SavedQueryTagsNotFoundError(value=value, valid=list(valid))
        return found if as_dataclass else [x.to_dict() for x in found]

    def get_tags_slow(self) -> t.List[str]:
        """Get all tags for saved queries.

        Examples:
            Get all known tags for all saved queries

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> data = apiobj.saved_query.get_tags()
            >>> len(data)
            19

        Returns:
            t.List[str]: list of all tags in use
        """
        tags = []
        for sq in self.get(as_dataclass=True):
            tags += [x for x in sq.tags if x not in tags]
        return tags

    @cached(cache=CACHE_TAGS)
    def get_tags(self) -> t.List[str]:
        """Get all tags for saved queries."""
        return self._get_tags().value

    @cached(cache=CACHE_RUN_BY)
    def get_query_history_run_by(self) -> t.List[str]:
        """Get the valid values for the run_by attribute for getting query history."""
        return self._get_query_history_run_by().value

    @cached(cache=CACHE_RUN_FROM)
    def get_query_history_run_from(self) -> t.List[str]:
        """Get the valid values for the run_from attribute for getting query history."""
        return self._get_query_history_run_from().value

    def get_query_history(
        self, generator: bool = False, **kwargs
    ) -> t.Union[t.Generator[models.QueryHistory, None, None], t.List[models.QueryHistory]]:
        """Get query history.

        Args:
            generator (bool, optional): Return a generator or a list
            **kwargs: passed to :meth:`get_fetch_history_generator`

        Returns:
            t.Union[t.Generator[QueryHistory, None, None], t.List[QueryHistory]]: t.Generator or
                list of query event models
        """
        gen = self.get_query_history_generator(**kwargs)
        return gen if generator else list(gen)

    # noinspection PyShadowingBuiltins
    def get_query_history_generator(
        self,
        run_by: t.Optional[PatternLikeListy] = None,
        run_from: t.Optional[PatternLikeListy] = None,
        tags: t.Optional[PatternLikeListy] = None,
        modules: t.Optional[PatternLikeListy] = None,
        name_term: t.Optional[str] = None,
        date_start: t.Optional[datetime.datetime] = None,
        date_end: t.Optional[datetime.datetime] = None,
        sort_attribute: t.Optional[str] = None,
        sort_descending: bool = False,
        search: t.Optional[str] = None,
        filter: t.Optional[str] = None,
        page_sleep: int = PagingState.page_sleep,
        page_size: int = PagingState.page_size,
        row_start: int = PagingState.row_start,
        row_stop: t.Optional[int] = PagingState.row_stop,
        log_level: t.Union[int, str] = PagingState.log_level,
        run_by_values: t.Optional[t.List[str]] = None,
        run_from_values: t.Optional[t.List[str]] = None,
        request_obj: t.Optional[models.QueryHistoryRequest] = None,
    ) -> t.List[models.QueryHistory]:
        """Get query history.

        Args:
            run_by (t.Optional[PatternLikeListy], optional): Filter records run by users
            run_from (t.Optional[PatternLikeListy], optional): Filter records run from api/gui
            tags (t.Optional[PatternLikeListy], optional): Filter records by SQ tags
            modules (t.Optional[PatternLikeListy], optional): Filter records by asset type
                (defaults to parent asset type)
            name_term (t.Optional[str], optional): Filter records by SQ name pattern
            date_start (t.Optional[datetime.datetime], optional): Filter records after this date
            date_end (t.Optional[datetime.datetime], optional): Filter records before this date
                (will default to now if date_start supplied and no date_end)
            sort_attribute (t.Optional[str], optional): Sort records based on this attribute
            sort_descending (bool, optional): Sort records descending or ascending
            search (t.Optional[str], optional): AQL search value to filter records
            filter (t.Optional[str], optional): AQL to filter records
            page_sleep (int, optional): Sleep N seconds between pages
            page_size (int, optional): Get N records per page
            row_start (int, optional): Start at row N
            row_stop (t.Optional[int], optional): Stop at row N
            log_level (t.Union[int, str], optional): log level to use for paging
            run_by_values (t.Optional[t.List[str]], optional): Output from
                :meth:`get_query_history_run_by` (will be fetched if not supplied)
            run_from_values (t.Optional[t.List[str]], optional): Output from
                :meth:`get_query_history_run_from` (will be fetched if not supplied)
            request_obj (t.Optional[QueryHistoryRequest], optional):  Request object to use
                for options
        """
        if not isinstance(request_obj, models.QueryHistoryRequest):
            request_obj = models.QueryHistoryRequest()

        request_obj.set_list(
            prop="run_from",
            values=run_from,
            enum=run_from_values,
            enum_callback=self.get_query_history_run_from,
        )
        request_obj.set_list(
            prop="run_by",
            values=run_by,
            enum=run_by_values,
            enum_callback=self.get_query_history_run_by,
        )
        request_obj.set_list(
            prop="tags",
            values=tags,
            enum_callback=self.get_tags,
        )
        # noinspection PyUnresolvedReferences
        request_obj.set_list(
            prop="modules",
            values=modules or self.parent.ASSET_TYPE,
            enum_callback=self.parent.asset_types,
        )
        request_obj.set_date(
            date_start=date_start,
            date_end=date_end,
        )
        request_obj.set_sort(
            value=sort_attribute,
            descending=sort_descending,
        )
        request_obj.set_name_term(
            value=name_term,
        )
        request_obj.set_search_filter(
            search=search,
            filter=filter,
        )
        with PagingState(
            purpose="Get Query History Events",
            page_sleep=page_sleep,
            page_size=page_size,
            row_start=row_start,
            row_stop=row_stop,
            log_level=log_level,
        ) as state:
            while not state.stop_paging:
                page = state.page(method=self._get_query_history, request_obj=request_obj)
                yield from page.rows

    def get(
        self, generator: bool = False, **kwargs
    ) -> t.Union[
        t.Generator[t.Union[dict, models.SavedQuery], None, None],
        t.List[t.Union[dict, models.SavedQuery]],
    ]:
        """Get all saved queries.

        Examples:
            Get all saved queries

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> data = apiobj.saved_query.get()
            >>> len(data)
            39

        Args:
            generator: return an iterator

        Yields:
            t.Generator[t.Union[dict, models.SavedQuery], None, None]: if generator = True,
                saved query dataclass or dict

        Returns:
            t.List[t.Union[dict, models.SavedQuery]]: if generator = False, list of saved query
                dataclass or dict

        """
        if "sqs" in kwargs:
            return kwargs["sqs"]

        gen = self.get_generator(**kwargs)

        if generator:
            return gen

        return list(gen)

    @cached(cache=CACHE_GET)
    def get_cached(self, **kwargs) -> t.List[t.Union[dict, models.SavedQuery]]:
        """Get all saved queries.

        Examples:
            Get all saved queries

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> data = apiobj.saved_query.get()
            >>> len(data)
            39

        Yields:
            t.Generator[QueryHistory, None, None]: if generator = True, saved query
                dataclass or dict

        Returns:
            t.List[t.Union[dict, models.SavedQuery]]: if generator = False, list of saved query
                dataclass or dict

        """
        return list(self.get_generator(**kwargs))

    # noinspection PyProtectedMember
    def get_cached_single(self, value: t.Union[str, dict, models.SavedQuery]) -> models.SavedQuery:
        """Pass."""
        name = models.SavedQuery._get_attr_value(value=value, attr="name")
        uuid = models.SavedQuery._get_attr_value(value=value, attr="uuid")
        items = self.get_cached(as_dataclass=True)
        for item in items:
            if name == item.name or uuid == item.uuid:
                return item

        raise SavedQueryNotFoundError(sqs=items, details=f"name={name!r} and uuid={value!r}")

    # noinspection PyUnresolvedReferences
    @property
    def query_by_asset_type(self) -> str:
        """Pass."""
        return f'module in ["{self.parent.ASSET_TYPE}"]'

    def build_filter_query(
        self,
        query: t.Optional[str] = None,
        add_query_by_asset_type: bool = True,
    ) -> t.Optional[str]:
        """Pass."""
        parts = []

        if isinstance(query, str) and query.strip():
            parts.append(query)

        if add_query_by_asset_type and not any([self.query_by_asset_type in x for x in parts]):
            parts.append(self.query_by_asset_type)
        return " and ".join(parts) if parts else None

    def get_generator(
        self,
        folder_id: str = "all",
        include_usage: bool = True,
        get_view_data: bool = True,
        as_dataclass: bool = AS_DATACLASS,
        page_sleep: int = 0,
        page_size: int = PAGE_SIZE,
        row_start: int = 0,
        row_stop: t.Optional[int] = None,
        add_query_by_asset_type: bool = True,
        log_level: t.Union[int, str] = LOG_LEVEL_API,
        query: t.Optional[str] = None,
        request_obj: t.Optional[models.SavedQueryGet] = None,
    ) -> t.Generator[models.SavedQuery, None, None]:
        """Get Saved Queries using a generator.

        Args:
            as_dataclass (bool, optional): Return saved query dataclass instead of dict
            folder_id (str, optional): folder id, will return all if "all", otherwise
                will return only saved queries directly in or under the folder
            include_usage (bool, optional): include usage data
            get_view_data (bool, optional): include view data
            page_sleep (int, optional): sleep in seconds between pages
            page_size (int, optional): page size
            row_start (int, optional): row start
            row_stop (int, optional): row stop
            add_query_by_asset_type (bool, optional): add query by asset type to query string
            log_level (int, optional): log level
            query (str, optional): query to filter saved queries
            request_obj (t.Optional[models.SavedQueryGet], optional): request object

        Yields:
            t.Generator[QueryHistory, None, None]: saved query dataclass or dict
        """
        query = self.build_filter_query(
            query=query, add_query_by_asset_type=add_query_by_asset_type
        )
        if not isinstance(request_obj, models.SavedQueryGet):
            request_obj = models.SavedQueryGet(
                filter=query,
                get_view_data=get_view_data,
                include_usage=include_usage,
                folder_id=folder_id,
            )

        purpose = f"Get Saved Queries using query: {query}"
        with PagingState(
            purpose=purpose,
            page_sleep=page_sleep,
            page_size=page_size,
            row_start=row_start,
            row_stop=row_stop,
            log_level=log_level,
        ) as state:
            while not state.stop_paging:
                page = state.page(method=self._get_model, request_obj=request_obj)
                for row in page.rows:
                    yield row if as_dataclass else row.to_dict()

    def add(self, as_dataclass: bool = AS_DATACLASS, **kwargs) -> t.Union[dict, models.SavedQuery]:
        """Create a saved query.

        Examples:
            Create a saved query using a :obj:`axonius_api_client.api.wizards.wizard.Wizard`

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> parsed = apiobj.wizard_text.parse(content="simple hostname contains blah")
            >>> query = parsed["query"]
            >>> expressions = parsed["expressions"]
            >>> sq = apiobj.saved_query.add(
            ...     name="test",
            ...     query=query,
            ...     expressions=expressions,
            ...     description="meep meep",
            ...     tags=["tag1", "tag2", "tag3"],
            ... )

        Notes:
            Saved Queries created without expressions will not be editable using the query wizard
            in the GUI. Use :obj:`axonius_api_client.api.wizards.wizard.Wizard` to produce a query
            and expressions for the GUI query wizard.

        Args:
            as_dataclass (bool, optional): return saved query dataclass or dict
            **kwargs: passed to :meth:`build_add_model`

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict

        """
        create_obj = self.build_add_model(**kwargs)
        self._check_name_exists(value=create_obj.name)
        added = self._add_from_dataclass(obj=create_obj)
        return self.get_by_uuid(value=added.id, as_dataclass=as_dataclass)

    def build_add_model(
        self,
        name: str,
        query: t.Optional[str] = None,
        wiz_entries: t.Optional[t.Union[t.List[dict], t.List[str], dict, str]] = None,
        tags: t.Optional[t.List[str]] = None,
        description: t.Optional[str] = None,
        expressions: t.Optional[t.List[str]] = None,
        fields: t.Optional[t.Union[t.List[str], str]] = None,
        fields_manual: t.Optional[t.Union[t.List[str], str]] = None,
        fields_regex: t.Optional[t.Union[t.List[str], str]] = None,
        fields_regex_root_only: bool = True,
        fields_fuzzy: t.Optional[t.Union[t.List[str], str]] = None,
        fields_default: bool = True,
        fields_root: t.Optional[str] = None,
        fields_parsed: t.Optional[t.Union[dict, t.List[str]]] = None,
        sort_field: t.Optional[str] = None,
        sort_descending: bool = True,
        sort_field_parsed: t.Optional[str] = None,
        field_filters: t.Optional[t.List[dict]] = None,
        excluded_adapters: t.Optional[t.List[dict]] = None,
        asset_excluded_adapters: t.Optional[t.List[dict]] = None,
        asset_filters: t.Optional[t.List[dict]] = None,
        gui_page_size: t.Optional[int] = None,
        private: bool = False,
        always_cached: bool = False,
        asset_scope: bool = False,
        folder: t.Optional[t.Union[str, FolderModel]] = None,
        create: bool = FolderDefaults.create_action,
        echo: bool = FolderDefaults.echo_action,
        enforcement_filter: t.Optional[str] = None,
        unique_adapters: bool = False,
        **kwargs,
    ) -> models.SavedQueryCreate:
        """Create a saved query.

        Examples:
            Create a saved query using a :obj:`axonius_api_client.api.wizards.wizard.Wizard`

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> wiz: str = "simple hostname contains blah"
            >>> parsed: dict = apiobj.wizard_text.parse(content=wiz)
            >>> sq_name: str = "test"
            >>> sq_query: str = parsed["query"]
            >>> sq_expressions: list[dict] = parsed["expressions"]
            >>> sq_description: str = "meep meep"
            >>> sq_tags: list[str] = ["nice1", "nice2", "nice3"]
            >>> sq = apiobj.saved_query.add(
            ...     name=sq_name,
            ...     query=sq_query,
            ...     expressions=sq_expressions,
            ...     description=sq_description,
            ...     tags=sq_tags,
            ...     as_dataclass=True,
            ... )

        Notes:
            Saved Queries created without expressions will not be editable using the query wizard
            in the GUI. Use :obj:`axonius_api_client.api.wizards.wizard.Wizard` to produce a query
            and it's accordant expressions for the GUI query wizard.

        Args:
            name: name of saved query
            description: description of saved query

            query: query built by GUI or API query wizard
            wiz_entries (t.Optional[t.Union[str, t.List[dict]]]): API query wizard entries to parse
                into query and GUI query wizard expressions
            tags (t.Optional[t.List[str]], optional): list of tags
            expressions (t.Optional[t.List[str]], optional): Expressions for GUI Query Wizard
            fields: fields to return for each asset (will be validated)
            fields_manual: fields to return for each asset (will NOT be validated)
            fields_regex: regex of fields to return for each asset
            fields_fuzzy: string to fuzzy match of fields to return for each asset
            fields_default: include the default fields defined in the parent asset object
            fields_regex_root_only: only match fields in fields_regex that are not sub-fields of
                other fields
            fields_root: include all fields of an adapter that are not complex sub-fields
            fields_parsed: previously parsed fields
            sort_field: sort the returned assets on a given field
            sort_descending: reverse the sort of the returned assets
            field_filters: field filters to apply to this query
            excluded_adapters: adapters to exclude from this query
            asset_excluded_adapters: adapters to exclude from this query
            asset_filters: asset filters to apply to this query
            gui_page_size: show N rows per page in GUI
            private: make this saved query private to current user
            always_cached: always keep this query cached
            asset_scope: make this query an asset scope query
            folder: folder to create saved query in
            create: create folder if it does not exist
            echo: echo folder actions to stdout/stderr
            sort_field_parsed: previously parsed sort field
            enforcement_filter: unknown
            unique_adapters: unknown

        Returns:
            models.SavedQueryCreate: saved query dataclass to create
        """
        asset_scope = coerce_bool(asset_scope)
        private = coerce_bool(private)
        always_cached = coerce_bool(always_cached)
        query_expr: t.Optional[str] = kwargs.get("query_expr", None) or query
        wiz_parsed: dict = self.parent.get_wiz_entries(wiz_entries=wiz_entries)

        root: FoldersModel = self.folders.get()
        fallback: t.Optional[FolderModel] = None
        if asset_scope:
            self.auth.CLIENT.data_scopes.check_feature_enabled()
            fallback: t.Optional[FolderModel] = root.path_asset_scope

        reason: str = f"Create Saved Query {name!r}"
        folder: FolderModel = root.resolve_folder(
            folder=folder,
            create=create,
            echo=echo,
            private=private,
            asset_scope=asset_scope,
            reason=reason,
            refresh=False,
            fallback=fallback,
        )

        if wiz_parsed:
            query = wiz_parsed["query"]
            query_expr = query
            expressions = wiz_parsed["expressions"]

        gui_page_size = check_gui_page_size(size=gui_page_size)

        if not isinstance(fields_parsed, (list, tuple)):
            fields_parsed = self.parent.fields.validate(
                fields=fields,
                fields_manual=fields_manual,
                fields_regex=fields_regex,
                fields_default=fields_default,
                fields_root=fields_root,
                fields_fuzzy=fields_fuzzy,
                fields_regex_root_only=fields_regex_root_only,
                fields_error=True,
            )
        if not isinstance(sort_field_parsed, str):
            sort_field_parsed: str = (
                self.parent.fields.get_field_name(value=sort_field) if sort_field else ""
            )

        view_query_meta: dict = {
            "enforcementFilter": enforcement_filter or "",
            "uniqueAdapters": unique_adapters,
        }
        view_query: dict = {
            "filter": query or "",
            "expressions": expressions or [],
            "search": None,
            "meta": view_query_meta,
            "onlyExpressionsFilter": query_expr or "",
        }
        view_sort: dict = {
            "desc": sort_descending,
            "field": sort_field_parsed or "",
        }
        view: dict = {
            "fields": fields_parsed,
            "pageSize": gui_page_size,
            "sort": view_sort,
            "query": view_query,
            "colFilters": listify(field_filters),
            "colExcludeAdapters": listify(excluded_adapters),
            "assetConditionExpressions": listify(asset_filters),
            "assetExcludeAdapters": listify(asset_excluded_adapters),
        }
        return models.SavedQueryCreate.new_from_kwargs(
            name=name,
            description=description,
            view=view,
            private=private,
            always_cached=always_cached,
            asset_scope=asset_scope,
            tags=tags,
            folder_id=folder.id,
        )

    def delete_by_name(
        self, value: str, as_dataclass: bool = AS_DATACLASS
    ) -> t.Union[dict, models.SavedQuery]:
        """Delete a saved query by name.

        Examples:
            Delete the saved query by name

            >>> import axonius_api_client as axonapi
            >>> connect_args: dict = axonapi.get_env_connect()
            >>> client: axonapi.Connect = axonapi.Connect(**connect_args)
            >>> apiobj: axonapi.api.assets.AssetMixin = client.devices
            >>>       # or client.users or client.vulnerabilities
            >>> deleted = apiobj.saved_query.delete_by_name(name="test")

        Args:
            value (str): name of saved query to delete
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
        """
        sq = self.get_by_name(value=value, as_dataclass=True)
        self._delete(uuid=sq.uuid)
        return sq if as_dataclass else sq.to_dict()

    def delete(
        self,
        rows: t.Union[t.List[MULTI], MULTI],
        errors: bool = True,
        refetch: bool = True,
        as_dataclass: bool = AS_DATACLASS,
        **kwargs,
    ) -> t.List[t.Union[dict, models.SavedQuery]]:
        """Delete saved queries.

        Args:
            rows (t.Union[t.List[MULTI], MULTI]): str or list of str with name, str or list of str
                with uuid, saved query dict or list of dict, or saved query dataclass or list
                of dataclass
            errors (bool, optional): Raise errors if SQ not found or other error
            refetch (bool, optional): refetch dataclass objects before deleting SQ
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.List[t.Union[dict, models.SavedQuery]]: list of saved query dataclass or dict that
                were deleted

        """
        do_echo = kwargs.get("do_echo", False)
        sqs = self.get(as_dataclass=True)
        deleted = []
        for row in listify(rows):
            try:
                sq = row
                if not isinstance(row, models.SavedQuery) or refetch:
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
    ) -> t.Union[dict, models.SavedQuery]:
        """Update a boolean flag for a SQ.

        Args:
            attr (str): attribute name
            sq (MULTI): saved query to update
            value (bool): value to set to attr
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
        """
        sq = self.get_by_multi(sq=sq, as_dataclass=True)
        value = coerce_bool(obj=value, errmsg=f"{attr} requires a valid boolean")
        setattr(sq, attr, value)
        return self._update_handler(sq=sq, as_dataclass=as_dataclass)

    def _update_handler(
        self, sq: models.SavedQuery, as_dataclass: bool = AS_DATACLASS
    ) -> t.Union[dict, models.SavedQuery]:
        """Update a SQ.

        Args:
            sq (MULTI): saved query to update
            as_dataclass (bool, optional): Return saved query dataclass instead of dict

        Returns:
            t.Union[dict, models.SavedQuery]: saved query dataclass or dict
        """
        ret = self._update_from_dataclass(obj=sq)
        return self.get_by_multi(sq=ret, as_dataclass=as_dataclass)

    def _update_from_dataclass(
        self, obj: models.SavedQueryMixins, uuid: t.Optional[str] = None
    ) -> models.SavedQuery:
        """Direct API method to update a saved query.

        Args:
            obj (models.SavedQueryMixins): pre-created dataclass

        Returns:
            models.SavedQuery: saved query dataclass
        """
        request_obj = models.SavedQueryMixins.create_from_other(obj)
        if not (isinstance(uuid, str) and uuid):
            uuid = getattr(obj, "uuid", None)
            if not (isinstance(uuid, str) and uuid):
                raise ApiError("Must supply UUID via uuid kwarg or obj.uuid")

        api_endpoint = ApiEndpoints.saved_queries.update
        response = api_endpoint.perform_request(
            http=self.auth.http,
            request_obj=request_obj,
            uuid=uuid,
        )
        self.get_cached.cache_clear()
        return response

    # noinspection PyUnresolvedReferences
    def _add_from_dataclass(self, obj: models.SavedQueryCreate) -> models.SavedQuery:
        """Direct API method to create a saved query.

        Args:
            obj (models.SavedQueryCreate): pre-created dataclass

        Returns:
            models.SavedQuery: saved query dataclass
        """
        api_endpoint = ApiEndpoints.saved_queries.create
        request_obj = models.SavedQuery.create_from_other(obj)
        response = api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, asset_type=self.parent.ASSET_TYPE
        )
        self.get_cached.cache_clear()
        return response

    def _delete(self, uuid: str) -> Metadata:
        """Direct API method to delete saved queries.

        Args:
            uuid (str): uuid of SQ to delete

        Returns:
            Metadata: Metadata object containing UUID of deleted SQ
        """
        api_endpoint = ApiEndpoints.saved_queries.delete
        request_obj = api_endpoint.load_request()
        response = api_endpoint.perform_request(
            http=self.auth.http, request_obj=request_obj, uuid=uuid
        )
        self.get_cached.cache_clear()
        return response

    def _get_model(self, request_obj: models.SavedQueryGet) -> t.List[models.SavedQuery]:
        """Direct API method to get all saved queries."""
        api_endpoint = ApiEndpoints.saved_queries.get
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _check_name_exists(self, value: str):
        """Check if a SQ already exists with a given name.

        Args:
            value (str): Name to check

        Raises:
            AlreadyExists: if SQ with name of value found
        """
        try:
            sq = self.get_by_name(value=value, as_dataclass=True)
            exc = AlreadyExists(f"Saved query with name or uuid of {value!r} already exists:\n{sq}")
            exc.obj = sq
            raise exc
        except SavedQueryNotFoundError:
            return

    def _get_query_history(
        self, request_obj: t.Optional[models.QueryHistoryRequest] = None
    ) -> t.List[models.QueryHistory]:
        """Pass."""
        api_endpoint = ApiEndpoints.saved_queries.get_query_history
        if not request_obj:
            request_obj = models.QueryHistoryRequest()
        return api_endpoint.perform_request(http=self.auth.http, request_obj=request_obj)

    def _get_query_history_run_by(self) -> ListValueSchema:
        """Get the valid values for the run_by attribute for getting query history."""
        api_endpoint = ApiEndpoints.saved_queries.get_run_by
        return api_endpoint.perform_request(http=self.auth.http)

    def _get_query_history_run_from(self) -> ListValueSchema:
        """Get the valid values for the run_from attribute for getting query history."""
        api_endpoint = ApiEndpoints.saved_queries.get_run_from
        return api_endpoint.perform_request(http=self.auth.http)

    # noinspection PyUnresolvedReferences
    def _get_tags(self) -> ListValueSchema:
        """Get the valid tags."""
        api_endpoint = ApiEndpoints.saved_queries.get_tags
        return api_endpoint.perform_request(http=self.auth.http, asset_type=self.parent.ASSET_TYPE)
